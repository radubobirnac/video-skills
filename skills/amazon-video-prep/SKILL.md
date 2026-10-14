---
name: amazon-video-prep
description: Check and prepare US Amazon Sponsored Brands, Sponsored Display, and product listing videos. Use for Amazon video specs, upload readiness, corrected MP4 exports, safe-zone and text review, opening hooks, and advertising claims. Use existing footage; exclude creating campaigns, uploading to Amazon, and generating new footage.
---

# Amazon Video Prep

Prepare existing video files for US Amazon placements. Combine deterministic file checks with an evidence-backed creative review. Preserve the original file.

## Inputs and scope

- Obtain the video, placement, marketplace, and intended ASIN/product. Infer supplied details rather than asking again. Default marketplace to US; ask for placement if it cannot be inferred.
- Select `sb-video` for horizontal Sponsored Brands, `sd-video` for horizontal Sponsored Display, or `listing-video` for Seller Central product-detail videos.
- Select `sb-store-vertical` only for a confirmed eligible Sponsored Brands Store campaign. Treat this profile as provisional until the current upload screen confirms its full requirements.
- Request an existing transcript when available. Use an available transcription tool if authorized; do not claim speech was reviewed from still frames. Do not require paid tools or keys for the core workflow.
- Read [placement requirements](references/amazon-requirements.md). Check current official placement and policy links before each live submission-prep task. Record the date, source disagreements, and upload-screen requirements supplied by the user. The included snapshot is dated, not a permanent guarantee.

## Run the workflow

Require Python 3.10+, `ffmpeg`, and `ffprobe` on PATH. Use Python subprocess argument lists; never build a shell command from a filename. Pillow is optional for annotated contact sheets (`python -m pip install Pillow`); individual frames work without it. Explain missing dependencies clearly.

Run from this skill's directory, or replace the script path with its absolute path. Choose a new output directory each time:

```bash
python scripts/amazon_video.py check /absolute/path/input.mp4 --placement sb-video --out /absolute/path/check-01
python scripts/amazon_video.py fix /absolute/path/input.mp4 --placement sd-video --out /absolute/path/export-01
python scripts/amazon_video.py check /absolute/path/input.mp4 --placement listing-video --out /absolute/path/listing-01 --transcript /absolute/path/transcript.srt
```

1. Inspect `report.md` and `report.json`. Separate `fail`, `warning`, and `unverified`. A conservative preference or unresolved source conflict is not a confirmed Amazon rejection.
2. Inspect individual frames, `frames.json`, and contact sheets when present. Review opening, ending, intermediate text, product visibility, and crop. Inspect additional timestamps or adjacent frames around suspected issues; sparse samples cannot prove the whole video is clean.
3. Complete [creative review](references/creative-review.md), with observed timestamps and evidence. Write `creative-review.md` in the output directory. Keep unreviewed audio, claims without substantiation, and unseen sections explicitly unverified. The script creates a checklist, not an automated creative approval.
4. Export a corrected copy if useful. `fix` transcodes, normalizes pixel shape, frame rate and encoding, and converts existing audio to AAC stereo at 48 kHz. Leave content and duration intact unless an explicit excerpt or crop is supplied. Do not synthesize audio, add disclosures, change captions, or rewrite claims automatically.
5. If the source is too long, select a coherent excerpt after reviewing footage/transcript. Specify `--start SECONDS --duration SECONDS`. Never silently cut the first 45 seconds or pad a short video.
6. If the source has the wrong aspect ratio, inspect product/text before choosing `--resize crop`. Never add letterboxing to an ad. If required dimensions exceed the source, use `--allow-upscale` only after noting that rescaling does not restore missing detail.
7. Inspect corrected frames and `corrected-report.md`, including crop, rescaling or audio conversion. A successful encode can still have technical failures or creative issues. The exporter rechecks its output and returns nonzero for remaining technical failures.

Example deliberate crop and excerpt:

```bash
python scripts/amazon_video.py fix /absolute/path/input.mp4 --placement sb-video --out /absolute/path/export-02 --start 12 --duration 20 --resize crop
```

Treat flags as explicit editing decisions. Do not pass cropping, excerpt, or upscale flags merely to make a report green. Use `--no-evidence` only for technical tests or when evidence is already available. If export is refused, retain the report and explain the needed decision.

## Deliver

Provide report, creative review, and corrected MP4 when produced. Include placement, source-check date, confirmed technical problems, changes made, remaining creative issues and unverified rules. Save user deliverables through the host's normal persistent file route.

Say "passes the checked technical rules; creative review still needed" when appropriate. Never claim Amazon approval, complete compliance, restored detail, or full speech/video review without evidence. Do not upload to Amazon or publish client footage to this public skill repository.
