# video-skills

Agent skills for video editing (SKILL.md format, works with Claude and Codex).

## Available skills

| Skill | Purpose | Requirements |
| --- | --- | --- |
| [amazon-video-prep](skills/amazon-video-prep/SKILL.md) | Check US Sponsored Brands, Sponsored Display and Seller Central listing videos; export corrected MP4s; guide an evidence-backed creative review | Python 3.10+, ffmpeg, ffprobe; optional Pillow |

The core tools run locally, use no API keys, and make no network calls. The assistant rechecks official Amazon requirements before a live submission-prep task. A report is not an Amazon approval guarantee.

## Install

Clone this repository, then copy the complete `skills/amazon-video-prep` directory to your agent's skill directory:

| Agent | Personal installation | Project installation | Invoke |
| --- | --- | --- | --- |
| Codex | `~/.agents/skills/amazon-video-prep` | `.agents/skills/amazon-video-prep` | `$amazon-video-prep` |
| Claude Code | `~/.claude/skills/amazon-video-prep` | `.claude/skills/amazon-video-prep` | `/amazon-video-prep` |

See the current official [OpenAI skill documentation](https://learn.chatgpt.com/docs/build-skills) and [Claude Code documentation](https://code.claude.com/docs/en/skills). For other hosts, use their documented skill import or installation flow. GitHub publication does not automatically install a skill in every chat environment.

Install ffmpeg from your OS package manager or its official distribution and make `ffmpeg` and `ffprobe` available on PATH. Optional annotated contact sheets require Pillow: `python -m pip install Pillow`. Without it, individual timestamped frames are still produced.

## Example request

> Use amazon-video-prep to check this US Sponsored Brands video, export a corrected copy where appropriate, and review its opening, text, safe zones and claims. Keep the original file.

## Direct command-line use

Run from the repository root. Choose a new output directory for every invocation.

```bash
python skills/amazon-video-prep/scripts/amazon_video.py check input.mp4 --placement sb-video --out output/check-01
python skills/amazon-video-prep/scripts/amazon_video.py fix input.mp4 --placement sd-video --out output/export-01
python skills/amazon-video-prep/scripts/amazon_video.py check input.mp4 --placement listing-video --out output/listing-01
```

`fix` preserves content and duration by default, re-encodes to H.264 Main/MP4, normalizes frame rate and pixel shape, converts existing audio to AAC stereo/48 kHz, and rechecks the result. It refuses arbitrary truncation, automatic padding, unrequested cropping or upscaling, and automatic HDR conversion. For a reviewed excerpt/crop, explicitly provide `--start`, `--duration`, `--resize crop`, or `--allow-upscale` as appropriate.

Outputs include Markdown/JSON technical reports, a creative-review checklist, sampled frames and optional contact sheets, plus a corrected MP4 and export decisions when produced. The agent must fill the creative review from evidence; the script does not perform OCR, speech transcription or comprehensive claims analysis. Exit code 0 means no confirmed technical failures (review items may remain); 1 means technical failures; 2 means a tool/input/export error.

## Scope and source uncertainty

The rules snapshot was checked on 2026-10-13. Display bitrate requirements conflict between two official pages, so the skill discloses the disagreement and exports above both targets. Listing requirements need confirmation against the current Seller Central upload screen. A provisional vertical Sponsored Brands Store profile is included, with incomplete rules explicitly marked for verification. Listing videos are not subjected to the ad profiles' 45-second limit.

The shaded lower-right contact-sheet guide is an internal review aid, not Amazon's official template. Review the actual placement template before judging safe zones. Sparse frame samples cannot certify an entire video. Resizing low-resolution material does not restore detail.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests generate synthetic media in a temporary directory; no client or copyrighted clips are bundled. Python, ffmpeg and ffprobe are required. Run the full suite after changing rules or encoding behavior.

## Contributing

Keep each skill under `skills/<name>/` with a concise `SKILL.md`, reusable scripts and source-backed references. Add meaningful regression tests for rule changes and file transformations. Do not commit client footage, transcripts, account details, credentials or generated outputs. Describe new dependencies and verify scripts on real media rather than only checking syntax.

MIT licensed; see [LICENSE](LICENSE).
