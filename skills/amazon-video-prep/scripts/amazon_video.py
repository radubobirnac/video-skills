#!/usr/bin/env python3
"""Local Amazon video checks and deliberate corrected exports. No network calls."""
from __future__ import annotations

import argparse
import fnmatch
import json
import math
import re
import shutil
import subprocess
import sys
from datetime import date
from fractions import Fraction
from pathlib import Path

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "profiles.json"
CATALOG = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
CREATIVE_ITEMS = ["Opening and product visibility", "Sound-off comprehension", "Text legibility and timing",
                  "Placement-specific safe zones", "Product and ASIN relevance", "Ending and pacing",
                  "Claims and substantiation", "Placement/category content policies", "Audio and US language",
                  "Crop, bars and source quality"]


class VideoError(Exception):
    pass


def run(cmd, timeout=600):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VideoError(f"Cannot run {cmd[0]}: {exc}") from exc
    if r.returncode:
        raise VideoError(f"{cmd[0]} failed: {r.stderr[-2500:]}")
    return r


def number(value, default=None):
    try:
        n = float(value)
        return n if math.isfinite(n) else default
    except (ValueError, TypeError):
        return default


def ratio(value, default=None):
    try:
        return float(Fraction(str(value).replace(":", "/")))
    except (ValueError, ZeroDivisionError):
        return default


def probe(path):
    raw = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]).stdout)
    videos = [s for s in raw.get("streams", []) if s.get("codec_type") == "video" and not s.get("disposition", {}).get("attached_pic")]
    if not videos:
        raise VideoError("No playable video stream found (an attached cover image does not count).")
    v = videos[0]
    audios = [s for s in raw.get("streams", []) if s.get("codec_type") == "audio"]
    a = audios[0] if audios else None
    duration = number(v.get("duration"), number(raw.get("format", {}).get("duration")))
    if not duration or duration <= 0:
        raise VideoError("Cannot establish a positive video duration.")
    rotation = number(v.get("tags", {}).get("rotate"), 0)
    for side in v.get("side_data_list", []):
        if "rotation" in side:
            rotation = number(side["rotation"], 0)
    w, h = int(v.get("width", 0)), int(v.get("height", 0))
    sar = ratio(v.get("sample_aspect_ratio"), 1) or 1
    display_w, display_h = w * sar, h
    if int(round(rotation)) % 180 == 90:
        w, h = h, w
        display_w, display_h = display_h, display_w
    return {"path": str(path), "bytes": path.stat().st_size, "duration": duration,
            "width": w, "height": h, "display_width": display_w, "display_height": display_h,
            "sar": sar, "rotation": rotation, "fps": ratio(v.get("avg_frame_rate")),
            "nominal_fps": ratio(v.get("r_frame_rate")), "video": v, "audio": a,
            "audio_stream_count": len(audios), "video_stream_count": len(videos),
            "format_name": raw.get("format", {}).get("format_name", "")}


def evaluate(m, placement):
    p = CATALOG["placements"][placement]
    checks = []

    def add(key, status, detail):
        checks.append({"id": key, "status": status, "detail": detail})

    for i, note in enumerate(p.get("notes", [])):
        add(f"source_note_{i}", "unverified", note)
    age = (date.today() - date.fromisoformat(CATALOG["checked_on"])).days
    if age > 90:
        add("dated_rules", "warning", f"Profile is {age} days old. Recheck official sources.")
    if "max_bytes" in p:
        add("file_size", "pass" if m["bytes"] <= p["max_bytes"] else "fail", f"{m['bytes']} bytes; snapshot limit {p['max_bytes']} bytes.")
    suffix = Path(m["path"]).suffix.lower()
    if "extensions" in p:
        preferred = p.get("container_preference_only", False)
        ext_ok = suffix in p["extensions"]
        actual_ok = bool({"mov", "mp4"} & set(m["format_name"].split(",")))
        status = "pass" if ext_ok and actual_ok else ("warning" if preferred else "fail")
        add("container", status, f"Extension {suffix}; actual container {m['format_name']}. " + ("MP4/MOV is an export preference." if preferred else "Require MP4/MOV extension and matching actual container."))
    for key, comparator in [("min_duration", lambda x, y: x >= y - .001), ("max_duration", lambda x, y: x <= y + .001)]:
        if key in p:
            add(key, "pass" if comparator(m["duration"], p[key]) else "fail", f"Video {m['duration']:.3f} s; {key.replace('_', ' ')} {p[key]} s.")
    if "aspect" in p:
        expected = p["aspect"][0] / p["aspect"][1]
        actual = m["display_width"] / m["display_height"]
        add("aspect", "pass" if abs(actual / expected - 1) < .001 else "fail", f"Display aspect {actual:.5f}; expected {p['aspect'][0]}:{p['aspect'][1]}.")
    dims = [m["width"], m["height"]]
    if "dimensions" in p:
        add("dimensions", "pass" if dims in p["dimensions"] else "fail", f"Autorotated dimensions {dims}; allowed {p['dimensions']}.")
    if "min_dimensions" in p:
        ok = all(x >= y for x, y in zip(dims, p["min_dimensions"]))
        add("dimensions", "pass" if ok else "fail", f"Autorotated dimensions {dims}; minimum {p['min_dimensions']}.")
    if placement == "listing-video" and (max(dims) > 1920 or min(dims) > 1080):
        add("listing_resolution", "warning", "Above the up-to-1080p listing recommendation; confirm console compatibility.")
    if "aspect" in p:
        add("pixel_shape", "pass" if abs(m["sar"] - 1) < .001 else "fail", f"Sample aspect ratio {m['sar']}; square pixels expected.")
    v = m["video"]
    if "video_codecs" in p:
        add("video_codec", "pass" if v.get("codec_name") in p["video_codecs"] else "fail", f"{v.get('codec_name')}; allowed {p['video_codecs']}.")
    if placement == "sb-video":
        pr = v.get("profile")
        add("video_profile", "unverified" if not pr else ("pass" if pr in ["Main", "Baseline", "Constrained Baseline"] else "fail"), f"Video profile {pr}; Main/Baseline expected.")
        field = v.get("field_order", "unknown")
        add("scan_type", "pass" if field == "progressive" else ("unverified" if field == "unknown" else "fail"), f"Scan type {field}; progressive expected.")
    if "fps" in p:
        f = m["fps"]
        add("frame_rate", "unverified" if f is None else ("pass" if any(abs(f - allowed) <= .011 for allowed in p["fps"]) else "fail"), f"Average fps {f}; allowed {p['fps']}.")
    if m["fps"] and m["nominal_fps"] and abs(m["fps"] / m["nominal_fps"] - 1) > .005:
        add("frame_rate_mode", "warning", "Average and nominal rates differ; possible VFR. This metadata heuristic does not certify constant frame rate.")
    for key in ["min_video_bps", "recommended_video_bps"]:
        if key not in p:
            continue
        b = number(v.get("bit_rate"))
        status = "unverified" if b is None else ("pass" if b >= p[key] else ("fail" if key.startswith("min_") else "warning"))
        add(key, status, f"Video stream bitrate {b}; {key.replace('_', ' ')} {p[key]}. Container bitrate is not substituted for video bitrate.")
    a = m["audio"]
    if a is None:
        add("audio_absent", "warning", "No audio stream. This is not automatically a technical failure; review sound-off meaning and any needed disclosure for ads.")
    else:
        codec = a.get("codec_name", "")
        if "audio_codecs" in p:
            add("audio_codec", "pass" if any(fnmatch.fnmatch(codec, x) for x in p["audio_codecs"]) else "fail", f"Audio codec {codec}; allowed {p['audio_codecs']}.")
            channels = int(a.get("channels", 0))
            add("audio_channels", "pass" if channels in [1, 2] else "fail", f"{channels} channels; mono or stereo expected.")
        for key in ["min_audio_bps", "recommended_audio_bps"]:
            if key not in p:
                continue
            b = number(a.get("bit_rate"))
            status = "unverified" if b is None else ("pass" if b >= p[key] else ("fail" if key.startswith("min_") else "warning"))
            add(key, status, f"Audio stream bitrate {b}; {key.replace('_', ' ')} {p[key]}.")
        sr = number(a.get("sample_rate"))
        if "min_sample_rate" in p:
            add("audio_sample_rate", "unverified" if sr is None else ("pass" if sr >= p["min_sample_rate"] else "fail"), f"Sample rate {sr}; minimum {p['min_sample_rate']}.")
        if "sample_rates" in p:
            add("audio_sample_rate", "pass" if sr in p["sample_rates"] else "fail", f"Sample rate {sr}; allowed {p['sample_rates']}.")
        ad = number(a.get("duration"))
        if ad and abs(ad - m["duration"]) > .25:
            add("audio_duration", "warning", "Audio and video durations differ by more than 0.25 s; inspect the ending.")
    if m["video_stream_count"] > 1 or m["audio_stream_count"] > 1:
        add("multiple_streams", "warning", "Multiple streams present; exporter uses the first playable video and first audio stream only.")
    if v.get("color_transfer") in ["smpte2084", "arib-std-b67"]:
        add("hdr", "warning", "HDR source requires a deliberate color workflow; this exporter refuses automatic HDR conversion.")
    return checks


def technical_status(checks):
    return "FAIL" if any(c["status"] == "fail" for c in checks) else ("REVIEW" if any(c["status"] in ["warning", "unverified"] for c in checks) else "PASS")


def black_intervals(path, m):
    """Only scan the first/last five seconds; report scope explicitly."""
    ranges = [(0, min(5, m["duration"]))]
    if m["duration"] > 5:
        ranges.append((max(5, m["duration"] - 5), min(5, m["duration"] - 5)))
    events = []
    for offset, length in ranges:
        r = run(["ffmpeg", "-hide_banner", "-nostdin", "-ss", str(offset), "-i", str(path), "-t", str(length),
                 "-map", f"0:{m['video']['index']}", "-an", "-vf", "blackdetect=d=0.08:pix_th=0.10:pic_th=0.98", "-f", "null", "-"])
        for start, end, duration in re.findall(r"black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)", r.stderr):
            events.append({"start": round(float(start) + offset, 3), "end": round(float(end) + offset, 3), "duration": float(duration)})
    return events


def transcript_flags(path):
    if not path:
        return []
    text = path.read_text(encoding="utf-8-sig")
    patterns = [r"\b(?:best|number one|#1|top[- ]selling|guaranteed|clinically proven|cures?|treats?|prevents?)\b",
                r"\b\d+(?:\.\d+)?\s*%", r"\b(?:act now|last chance|limited time|save \d+|discount|five stars?)\b"]
    return [{"phrase": match.group(), "context": text[max(0, match.start() - 90):match.end() + 90]}
            for pattern in patterns for match in re.finditer(pattern, text, re.I)]


def evidence(path, m, out, placement):
    folder = out / "frames"
    folder.mkdir()
    end = max(0, m["duration"] - max(.1, 2 / (m["fps"] or 30)))
    stamps = sorted({round(min(t, end), 3) for t in [0, .5, 1, 2, 3, max(0, end - 1), end] + [end * i / 8 for i in range(1, 8)]})
    records = []
    for i, t in enumerate(stamps):
        name = f"frame-{i:02d}-{t:08.3f}s.jpg"
        target = folder / name
        run(["ffmpeg", "-v", "error", "-nostdin", "-n", "-ss", str(t), "-i", str(path), "-map", f"0:{m['video']['index']}",
             "-frames:v", "1", "-vf", "scale=640:-2", "-threads", "1", "-q:v", "3", str(target)])
        if not target.is_file():
            raise VideoError(f"No frame decoded at {t:.3f}s.")
        records.append({"requested_seconds": t, "file": f"frames/{name}"})
    (out / "frames.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return records, "Pillow unavailable; inspect individual frames instead of a contact sheet."
    tile_w, tile_h = 360, 240
    for guided in [False, True] if placement != "listing-video" else [False]:
        sheet = Image.new("RGB", (tile_w * 4, tile_h * math.ceil(len(records) / 4)), "#eef1f4")
        draw = ImageDraw.Draw(sheet)
        for i, rec in enumerate(records):
            im = Image.open(out / rec["file"]).convert("RGB")
            im.thumbnail((tile_w - 12, tile_h - 44))
            if guided:
                overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
                d = ImageDraw.Draw(overlay)
                d.rectangle((int(im.width * .8), int(im.height * .75), im.width - 1, im.height - 1), fill=(255, 40, 40, 90), outline=(255, 0, 0, 255))
                im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
            x, y = (i % 4) * tile_w, (i // 4) * tile_h
            sheet.paste(im, (x + 6, y + 4))
            draw.text((x + 6, y + tile_h - 35), f"{rec['requested_seconds']:.3f}s (requested seek)", fill="black")
            if guided:
                draw.text((x + 6, y + tile_h - 20), "Internal guide - verify official template", fill="#991b1b")
        sheet.save(out / ("contact-sheet-guide.jpg" if guided else "contact-sheet.jpg"), quality=90)
    return records, None


def report(path, m, placement, out, transcript=None, no_evidence=False, prefix=""):
    checks = evaluate(m, placement)
    evidence_note = None
    if not no_evidence:
        events = black_intervals(path, m)
        checks.append({"id": "black_frame_scan", "status": "warning" if events else "pass",
                       "detail": "Heuristic first/last-five-second black scan only; dark footage can be a false positive.", "intervals": events})
        _, evidence_note = evidence(path, m, out, placement)
    flags = transcript_flags(transcript)
    if flags:
        checks.append({"id": "transcript_flags", "status": "warning", "detail": "Claim/ad-policy-like phrases need contextual review; no text has been automatically cleared.", "matches": flags})
    r = {"placement": placement, "marketplace": "US", "requirements_checked_on": CATALOG["checked_on"],
         "technical_status": technical_status(checks), "creative_status": "unreviewed", "approval_status": "not_assessed",
         "input": m, "checks": checks, "evidence_note": evidence_note, "transcript_supplied": bool(transcript),
         "sources": {k: CATALOG["sources"][k] for k in CATALOG["placements"][placement]["source_ids"]}}
    (out / f"{prefix}report.json").write_text(json.dumps(r, indent=2), encoding="utf-8")
    lines = [f"# {CATALOG['placements'][placement]['label']}", "", f"Technical status: **{r['technical_status']}**",
             "Creative status: **unreviewed**. Amazon approval is not assessed.", "", f"Requirements snapshot: {CATALOG['checked_on']} · US", "",
             f"Video: {m['width']}×{m['height']} · {m['duration']:.3f} s · {m['fps']} fps · {m['bytes']} bytes", "",
             "| Check | Result | Detail |", "| --- | --- | --- |"]
    for c in checks:
        detail = c["detail"].replace("|", "\\|").replace("\n", " ")
        if c.get("intervals"):
            detail += " Intervals: " + ", ".join(f"{e['start']}–{e['end']}s" for e in c["intervals"])
        lines.append(f"| {c['id']} | {c['status']} | {detail} |")
    lines += ["", "## Creative evidence", "", "Inspect individual frames and frames.json. Seek times are requested timestamps, not exact decoded-frame PTS. Sampling cannot certify the full clip.",
              "The shaded contact sheet is an internal review guide, not an official safe-zone template.", "No OCR, transcription or full audio/content review was performed by this script."]
    if flags:
        lines += ["", "## Transcript flags (contextual review required)", ""]
        for f in flags:
            lines.append(f"- {f['phrase']!r}: {f['context']!r}")
    if evidence_note:
        lines += ["", evidence_note]
    lines += ["", "## Official references", ""] + [f"- [{k}]({u})" for k, u in r["sources"].items()]
    (out / f"{prefix}report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not (out / "creative-review.md").exists():
        review = ["# Creative review", "", "Status: unreviewed. Replace each unverified entry with timestamped evidence after inspection.", "",
                  "| Item | Result | Evidence / action |", "| --- | --- | --- |"]
        review += [f"| {item} | unverified | |" for item in CREATIVE_ITEMS]
        (out / "creative-review.md").write_text("\n".join(review) + "\n", encoding="utf-8")
    return r


def export_plan(m, args):
    p = CATALOG["placements"][args.placement]
    duration = args.duration if args.duration is not None else m["duration"] - args.start
    if args.start < 0 or duration <= 0 or args.start + duration > m["duration"] + .001:
        raise VideoError("Select a positive excerpt entirely within the source video.")
    if p.get("min_duration") and duration < p["min_duration"]:
        raise VideoError("Video/excerpt is too short; provide enough actual footage. Padding is not automatic.")
    if p.get("max_duration") and duration > p["max_duration"] + .001:
        raise VideoError("Select a coherent excerpt with --start and --duration; automatic truncation is disabled.")
    if m["video"].get("color_transfer") in ["smpte2084", "arib-std-b67"]:
        raise VideoError("HDR conversion requires a deliberate color-managed workflow; automatic export is refused.")
    dw, dh = m["display_width"], m["display_height"]
    if "aspect" in p:
        aspect = p["aspect"][0] / p["aspect"][1]
        if abs((dw / dh) / aspect - 1) >= .001 and args.resize != "crop":
            raise VideoError("Aspect ratio differs. Review composition, then explicitly use --resize crop if suitable.")
        if "dimensions" in p:
            candidates = [d for d in p["dimensions"] if d[0] <= dw + 1 and d[1] <= dh + 1]
            # Prefer 1080p when available; retain 720p if that avoids upscaling.
            target = candidates[min(1, len(candidates) - 1)] if candidates else p["dimensions"][0]
        else:
            target = p["min_dimensions"]
    else:
        factor = min(1, 1920 / max(dw, dh), 1080 / min(dw, dh))
        target = [max(2, int(dw * factor) // 2 * 2), max(2, int(dh * factor) // 2 * 2)]
    upscale = target[0] > dw + 1 or target[1] > dh + 1
    if upscale and not args.allow_upscale:
        raise VideoError("Target exceeds source detail. Use --allow-upscale after reviewing quality, or supply a higher-resolution source.")
    bps = p["export_video_bps"]
    if "max_bytes" in p:
        budget = int(p["max_bytes"] * .85 * 8 / duration) - (192000 if m["audio"] else 0)
        bps = min(bps, budget)
        floor = p.get("recommended_video_bps", p.get("min_video_bps", 500000))
        if bps < floor:
            raise VideoError("Duration/file-size budget cannot meet the conservative quality target; select a shorter excerpt.")
    filters = []
    if m["video"].get("field_order") not in [None, "unknown", "progressive"]:
        filters.append("yadif")
    filters += ["scale=trunc(iw*sar/2)*2:ih", "setsar=1", f"scale={target[0]}:{target[1]}:force_original_aspect_ratio=increase",
                f"crop={target[0]}:{target[1]}", "setsar=1", f"fps={p['export_fps']}", "format=yuv420p"]
    # A 45 s source at 29.97 fps can otherwise become 45.011 s after rounding.
    fps = ratio(p["export_fps"])
    frames = math.ceil(duration * fps - 1e-8)
    if p.get("max_duration"):
        frames = min(frames, math.floor(p["max_duration"] * fps + 1e-8))
    if p.get("min_duration"):
        frames = max(frames, math.ceil(p["min_duration"] * fps - 1e-8))
    return {"start": args.start, "duration": duration, "target_dimensions": target, "upscaled": upscale,
            "resize": args.resize, "fps": p["export_fps"], "video_bps": bps, "filters": filters,
            "max_video_frames": frames, "frame_quantized_duration": frames / fps,
            "notes": ["Rescaling does not restore missing detail.", "First video/audio streams only; review converted audio and composition."]}


def fix(path, m, args, out):
    plan = export_plan(m, args)
    (out / "export-plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    target = out / "corrected.mp4"
    cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-n", "-ss", str(plan["start"]), "-i", str(path), "-t", str(plan["duration"]),
           "-map", f"0:{m['video']['index']}"]
    if m["audio"]:
        cmd += ["-map", f"0:{m['audio']['index']}"]
    cmd += ["-map_metadata", "-1", "-vf", ",".join(plan["filters"]), "-c:v", "libx264", "-profile:v", "main", "-preset", "fast",
            "-b:v", str(plan["video_bps"]), "-minrate", str(plan["video_bps"]), "-maxrate", str(plan["video_bps"]),
            "-bufsize", str(plan["video_bps"] * 2), "-x264-params", "nal-hrd=cbr:force-cfr=1", "-threads", "2"]
    if m["audio"]:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
    else:
        cmd += ["-an"]
    cmd += ["-frames:v", str(plan["max_video_frames"]), "-metadata:s:v:0", "rotate=0", "-movflags", "+faststart", str(target)]
    (out / "ffmpeg-command.json").write_text(json.dumps(cmd, indent=2), encoding="utf-8")
    result = run(cmd, timeout=3600)
    (out / "encode.log").write_text(result.stderr, encoding="utf-8")
    corrected = probe(target)
    evidence_dir = out / "corrected-evidence"
    evidence_dir.mkdir()
    r = report(target, corrected, args.placement, evidence_dir, args.transcript, args.no_evidence)
    r["evidence_directory"] = "corrected-evidence"
    (out / "corrected-report.json").write_text(json.dumps(r, indent=2), encoding="utf-8")
    text = (evidence_dir / "report.md").read_text(encoding="utf-8")
    text += "\nCorrected evidence is in `corrected-evidence/` (source evidence remains in the parent output directory).\n"
    (out / "corrected-report.md").write_text(text, encoding="utf-8")
    return r


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "fix"])
    parser.add_argument("input", type=Path)
    parser.add_argument("--placement", required=True, choices=list(CATALOG["placements"]))
    parser.add_argument("--out", required=True, type=Path, help="New output directory; existing directories are refused.")
    parser.add_argument("--transcript", type=Path, help="Existing UTF-8 txt/SRT/VTT; heuristic flags only.")
    parser.add_argument("--start", type=float, default=0)
    parser.add_argument("--duration", type=float)
    parser.add_argument("--resize", choices=["preserve", "crop"], default="preserve")
    parser.add_argument("--allow-upscale", action="store_true")
    parser.add_argument("--no-evidence", action="store_true")
    args = parser.parse_args(argv)
    if not math.isfinite(args.start) or (args.duration is not None and not math.isfinite(args.duration)):
        parser.error("Start/duration must be finite numbers.")
    for tool in ["ffmpeg", "ffprobe"]:
        if not shutil.which(tool):
            print(f"ERROR: Install {tool} and make it available on PATH.", file=sys.stderr)
            return 2
    out = args.out.resolve()
    try:
        path = args.input.resolve(strict=True)
        if not path.is_file():
            raise VideoError("Input must be a local video file.")
        if args.transcript:
            args.transcript = args.transcript.resolve(strict=True)
        m = probe(path)
        out.mkdir(parents=True, exist_ok=False)
        r = report(path, m, args.placement, out, args.transcript, args.no_evidence)
        if args.action == "fix":
            r = fix(path, m, args, out)
        print(json.dumps({"technical_status": r["technical_status"], "creative_status": "unreviewed", "output_directory": str(out)}))
        return 1 if r["technical_status"] == "FAIL" else 0
    except (VideoError, OSError, ValueError, json.JSONDecodeError) as exc:
        # Never write into an output folder that predates this invocation.
        if 'r' in locals() and out.is_dir():
            (out / "export-error.txt").write_text(str(exc) + "\n", encoding="utf-8")
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
