"""Real-media regression tests; generate fixtures locally and commit no footage."""
import argparse
import copy
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
SKILL = Path(os.environ.get("AMAZON_VIDEO_SKILL", str(HERE.parents[1] / "skills" / "amazon-video-prep")))
SPEC = importlib.util.spec_from_file_location("amazon_video", SKILL / "scripts" / "amazon_video.py")
video = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(video)


class VideoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="amazon-video-test-")
        cls.root = Path(cls.tmp.name)
        cls.clip = cls.root / "client $clip; quoted.mp4"
        video.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=30",
                   "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=32000", "-t", "6",
                   "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac",
                   "-b:a", "64k", "-threads", "2", str(cls.clip)])
        cls.metadata = video.probe(cls.clip)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def args(self, **kwargs):
        a = dict(placement="sb-video", start=0, duration=None, resize="preserve", allow_upscale=False,
                 transcript=None, no_evidence=True, marketplace="US", content_language=None)
        a.update(kwargs)
        return argparse.Namespace(**a)

    def test_source_is_real_and_audio_errors_detected(self):
        checks = {c["id"]: c for c in video.evaluate(self.metadata, "sb-video")}
        self.assertEqual(checks["dimensions"]["status"], "pass")
        self.assertEqual(checks["audio_sample_rate"]["status"], "fail")
        self.assertEqual(checks["min_audio_bps"]["status"], "fail")

    def test_corrected_export_rechecked_and_original_preserved(self):
        before = self.clip.read_bytes()
        out = self.root / "fixed"
        out.mkdir()
        result = video.fix(self.clip, self.metadata, self.args(), out)
        self.assertNotEqual(result["technical_status"], "FAIL")
        m = video.probe(out / "corrected.mp4")
        self.assertEqual(m["video"]["profile"], "Main")
        self.assertEqual(int(m["audio"]["sample_rate"]), 48000)
        self.assertEqual(self.clip.read_bytes(), before)
        self.assertEqual(result["creative_status"], "unreviewed")
        self.assertEqual(result["evidence_directory"], "corrected-evidence")
        self.assertIn("corrected-evidence/", (out / "corrected-report.md").read_text())

    def test_ads_and_listing_have_distinct_duration_rules(self):
        m = copy.deepcopy(self.metadata)
        m["duration"] = 61
        ad = video.evaluate(m, "sb-video")
        listing = video.evaluate(m, "listing-video")
        self.assertTrue(any(c["id"] == "max_duration" and c["status"] == "fail" for c in ad))
        self.assertFalse(any(c["id"] in ["min_duration", "max_duration"] for c in listing))
        self.assertEqual(video.export_plan(m, self.args(placement="listing-video"))["duration"], 61)

    def test_long_ads_need_deliberate_excerpt(self):
        m = copy.deepcopy(self.metadata)
        m["duration"] = 61
        with self.assertRaises(video.VideoError):
            video.export_plan(m, self.args())
        plan = video.export_plan(m, self.args(start=12, duration=20))
        self.assertEqual(plan["start"], 12)
        self.assertEqual(plan["duration"], 20)

    def test_short_video_is_not_padded(self):
        m = copy.deepcopy(self.metadata)
        m["duration"] = 4
        with self.assertRaises(video.VideoError):
            video.export_plan(m, self.args())

    def test_crop_and_upscale_require_explicit_flags(self):
        m = copy.deepcopy(self.metadata)
        m.update(width=1080, height=1920, display_width=1080, display_height=1920)
        with self.assertRaises(video.VideoError):
            video.export_plan(m, self.args())
        with self.assertRaises(video.VideoError):
            video.export_plan(self.metadata, self.args(placement="sd-video"))
        plan = video.export_plan(self.metadata, self.args(placement="sd-video", allow_upscale=True))
        self.assertTrue(plan["upscaled"])

    def test_silent_ads_are_review_not_missing_audio_failure(self):
        m = copy.deepcopy(self.metadata)
        m["audio"] = None
        checks = video.evaluate(m, "sb-video")
        self.assertTrue(any(c["id"] == "audio_absent" and c["status"] == "warning" for c in checks))
        self.assertFalse(any(c["id"] == "audio_absent" and c["status"] == "fail" for c in checks))

    def test_display_source_conflict_is_disclosed(self):
        m = copy.deepcopy(self.metadata)
        m["video"]["bit_rate"] = "2000000"
        m["audio"]["bit_rate"] = "128000"
        checks = {c["id"]: c for c in video.evaluate(m, "sd-video")}
        self.assertEqual(checks["min_video_bps"]["status"], "pass")
        self.assertEqual(checks["recommended_video_bps"]["status"], "warning")
        self.assertEqual(checks["source_note_0"]["status"], "unverified")

    def test_disguised_container_detected(self):
        m = copy.deepcopy(self.metadata)
        m["format_name"] = "avi"
        self.assertTrue(any(c["id"] == "container" and c["status"] == "fail" for c in video.evaluate(m, "sb-video")))

    def test_missing_video_bitrate_is_not_replaced_by_container_bitrate(self):
        m = copy.deepcopy(self.metadata)
        m["video"].pop("bit_rate", None)
        self.assertTrue(any(c["id"] == "min_video_bps" and c["status"] == "unverified" for c in video.evaluate(m, "sb-video")))

    def test_existing_directory_refused(self):
        out = self.root / "existing"
        out.mkdir()
        marker = out / "keep.txt"
        marker.write_text("keep", encoding="utf-8")
        result = video.main(["check", str(self.clip), "--placement", "sb-video", "--out", str(out), "--no-evidence"])
        self.assertEqual(result, 2)
        self.assertEqual(marker.read_text(), "keep")
        self.assertFalse((out / "report.json").exists())

    def test_transcript_flags_are_not_approval(self):
        text = self.root / "claims.srt"
        text.write_text("1\n00:00:01,000 --> 00:00:03,000\nClinically proven to prevent decay. Save 50%.\n", encoding="utf-8")
        flags = video.transcript_flags(text)
        self.assertGreaterEqual(len(flags), 3)
        self.assertIn("00:00:01", flags[0]["context"])

    def test_frames_and_creative_checklist_generated(self):
        out = self.root / "evidence"
        out.mkdir()
        r = video.report(self.clip, self.metadata, "sb-video", out)
        frames = json.loads((out / "frames.json").read_text())
        self.assertGreater(len(frames), 6)
        self.assertTrue((out / frames[0]["file"]).is_file())
        self.assertIn("unverified", (out / "creative-review.md").read_text())
        self.assertEqual(r["approval_status"], "not_assessed")

    def test_display_export_at_max_duration(self):
        clip = self.root / "display-45.mp4"
        video.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=blue:size=1920x1080:rate=30",
                   "-t", "45", "-c:v", "libx264", "-preset", "ultrafast", "-threads", "2", str(clip)])
        out = self.root / "display-fixed"
        out.mkdir()
        r = video.fix(clip, video.probe(clip), self.args(placement="sd-video"), out)
        self.assertNotEqual(r["technical_status"], "FAIL")
        self.assertLessEqual(r["input"]["duration"], 45.001)

    def test_accepted_frame_rates_are_kept(self):
        for placement, rate, expected in [("sb-video", "25", "25/1"), ("sb-video", "24000/1001", "24000/1001"),
                                          ("listing-video", "25", "25/1"), ("sd-video", "30", "30000/1001")]:
            with self.subTest(placement=placement, rate=rate):
                clip = self.root / f"rate-{placement}-{rate.replace('/', '_')}.mp4"
                video.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", f"color=c=gray:size=1920x1080:rate={rate}",
                           "-t", "6", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-threads", "2", str(clip)])
                out = self.root / f"rate-fixed-{placement}-{rate.replace('/', '_')}"
                out.mkdir()
                r = video.fix(clip, video.probe(clip), self.args(placement=placement), out)
                self.assertEqual(r["input"]["video"]["avg_frame_rate"], expected)
                self.assertNotEqual(r["technical_status"], "FAIL")

    def test_listing_export_preserves_duration_over_ad_limit(self):
        clip = self.root / "listing-61.mp4"
        video.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=green:size=320x180:rate=30",
                   "-t", "61", "-c:v", "libx264", "-preset", "ultrafast", "-threads", "2", str(clip)])
        out = self.root / "listing-fixed"
        out.mkdir()
        r = video.fix(clip, video.probe(clip), self.args(placement="listing-video"), out)
        self.assertNotEqual(r["technical_status"], "FAIL")
        self.assertAlmostEqual(r["input"]["duration"], 61, places=2)

    def test_rotation_normalized_without_double_rotation(self):
        clip = self.root / "rotated.mp4"
        help_text = video.run(["ffmpeg", "-hide_banner", "-h", "full"]).stdout
        if "-display_rotation" in help_text:
            cmd = ["ffmpeg", "-v", "error", "-display_rotation:v:0", "90", "-i", str(self.clip), "-c", "copy", str(clip)]
        else:
            cmd = ["ffmpeg", "-v", "error", "-i", str(self.clip), "-c", "copy", "-metadata:s:v:0", "rotate=90", str(clip)]
        video.run(cmd)
        m = video.probe(clip)
        self.assertEqual([m["width"], m["height"]], [720, 1280])
        out = self.root / "rotation-fixed"
        out.mkdir()
        r = video.fix(clip, m, self.args(placement="listing-video"), out)
        self.assertEqual([r["input"]["width"], r["input"]["height"]], [720, 1280])
        self.assertEqual(r["input"]["rotation"], 0)

    def test_marketplace_sources_use_correct_country(self):
        for market, prefix, seller in [("UK", "en-gb", "sellercentral.amazon.co.uk"), ("CA", "en-ca", "sellercentral.amazon.ca")]:
            with self.subTest(market=market):
                self.assertIn(f"/{prefix}/", video.source_links("sb-video", market)["sb"])
                self.assertIn(f"/{prefix}/", video.source_links("sd-video", market)["sd"])
                self.assertIn(seller, video.source_links("listing-video", market)["listing"])

    def test_marketplace_overrides_do_not_mutate_shared_rules(self):
        ca = video.placement_profile("listing-video", "CA")
        ca["notes"].append("temporary test change")
        self.assertNotIn("temporary test change", video.placement_profile("listing-video", "US")["notes"])
        self.assertNotIn("temporary test change", video.placement_profile("listing-video", "CA")["notes"])

    def test_uk_and_canada_corrected_exports_keep_marketplace(self):
        for market, locale, store in [("UK", "en-GB", "amazon.co.uk"), ("CA", "en-CA", "amazon.ca")]:
            with self.subTest(market=market):
                out = self.root / f"fixed-{market}"
                out.mkdir()
                r = video.fix(self.clip, self.metadata, self.args(marketplace=market, content_language=locale), out)
                self.assertNotEqual(r["technical_status"], "FAIL")
                self.assertEqual(r["marketplace"], market)
                self.assertEqual(r["store"], store)
                self.assertEqual(r["target_locale"], locale)
                self.assertEqual(r["declared_content_language"], locale)
                plan = json.loads((out / "export-plan.json").read_text())
                self.assertEqual(plan["marketplace"], market)
                self.assertIn(locale, (out / "corrected-evidence" / "creative-review.md").read_text())

    def test_french_canadian_declaration_is_not_auto_approved(self):
        checks = {c["id"]: c for c in video.evaluate(self.metadata, "sb-video", "CA", "fr-CA")}
        self.assertEqual(checks["declared_ad_language"]["status"], "warning")
        self.assertEqual(checks["language_review"]["status"], "unverified")
        self.assertIn("not detected/verified", checks["language_review"]["detail"])

    def test_cli_default_us_and_case_insensitive_country_selection(self):
        for flag, expected in [([], "US"), (["--marketplace", "uk"], "UK"), (["--marketplace", "ca"], "CA")]:
            with self.subTest(market=expected):
                out = self.root / f"cli-{expected}"
                rc = video.main(["check", str(self.clip), "--placement", "sb-video", "--out", str(out), "--no-evidence"] + flag)
                self.assertEqual(rc, 1)  # Existing fixture has known audio failures.
                report = json.loads((out / "report.json").read_text())
                self.assertEqual(report["marketplace"], expected)

    def test_unsupported_marketplace_refused_before_writing(self):
        out = self.root / "unsupported"
        with self.assertRaises(SystemExit) as exc:
            video.main(["check", str(self.clip), "--placement", "sb-video", "--marketplace", "DE", "--out", str(out)])
        self.assertEqual(exc.exception.code, 2)
        self.assertFalse(out.exists())

    def test_standard_metadata_preserved_and_xmp_not_certified(self):
        clip = self.root / "with-title.mp4"
        video.run(["ffmpeg", "-v", "error", "-i", str(self.clip), "-c", "copy", "-metadata", "title=Original title", str(clip)])
        out = self.root / "metadata-fixed"
        out.mkdir()
        r = video.fix(clip, video.probe(clip), self.args(placement="listing-video", marketplace="UK"), out)
        self.assertEqual(r["input"]["format_tags"].get("title"), "Original title")
        checks = {c["id"]: c for c in r["checks"]}
        self.assertEqual(checks["required_metadata"]["status"], "unverified")


if __name__ == "__main__":
    unittest.main()
