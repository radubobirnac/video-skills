# Amazon agent skills

Reusable skills for Amazon video preparation, report validation and PPC bulk file QA (SKILL.md format, works with Claude and Codex).

## Available skills

| Skill | Purpose | Requirements |
| --- | --- | --- |
| [amazon-report-preflight](skills/amazon-report-preflight/SKILL.md) | Validate US, UK and Canadian campaign, search-term, targeting, advertised-product, Business Report and bulk exports; normalize usable data and report exceptions | Python 3.10+; optional openpyxl for XLSX |
| [amazon-ppc-bulk-qa](skills/amazon-ppc-bulk-qa/SKILL.md) | Check SP keyword/negative creates, bid and budget edits against fresh US/UK/CA bulk exports; preserve IDs/names and stage harvesting safely | Python 3.10+, openpyxl |
| [amazon-video-prep](skills/amazon-video-prep/SKILL.md) | Check US, UK and Canadian Sponsored Brands, Sponsored Display and listing videos; export corrected MP4s; guide creative and localization review | Python 3.10+, ffmpeg, ffprobe; optional Pillow |

These skills are early releases tested with synthetic fixtures. Real client-export and real-ad validation remain pending.

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

For other destinations, specify "UK" or "Canada" in the request. The assistant uses the same skill with the corresponding marketplace profile. No real client-ad validation has been performed yet.

## Report preflight

Copy the complete `skills/amazon-report-preflight` folder to the same agent-specific skill locations above, using `amazon-report-preflight` as the folder name. XLSX reading needs `python -m pip install openpyxl`; CSV/TSV use Python's standard library.

Example request:

> Use amazon-report-preflight to check these Amazon reports before analysis. Preserve the originals, normalize usable data, and explain duplicate rows, date/currency conflicts, attribution definitions and ASIN-join limits.

Run from the repository root:

```bash
python skills/amazon-report-preflight/scripts/report_preflight.py search-terms.csv --as-of 2026-10-13 --out output/report-inspect-01
python skills/amazon-report-preflight/scripts/report_preflight.py --manifest manifest.json --out output/report-check-01
```

Replace the example review date with the applicable date. First inspection writes a draft manifest and reports unknown context. Fill the manifest from supplied evidence, then rerun. See [manifest and outputs](skills/amazon-report-preflight/references/manifest-and-outputs.md).

The checker supports CSV, TSV, TXT and XLSX exports; keeps IDs as text and amounts as exact decimals; retains source file/sheet/row lineage; and separates READY, NEEDS_CONTEXT and BLOCKED reports. Outputs include Markdown/JSON findings, an exception CSV, a canonical audit CSV, an analysis-ready CSV and comparison/join checks. It never changes sources, converts FX, fabricates missing values, pools report types, or labels retail sales minus attributed sales exact organic revenue. CSV formula-like text is escaped; original cell text remains in audit JSON.

Exact repeated rows block analysis by default. Explicit `--dedupe-exact` retains the first exact row and logs removed copies. Mixed-ASIN groups remain unresolved; current bulk configuration does not prove historical attribution. Partial, blocked reports contribute no analysis-ready rows or totals.

Exit codes: 0 READY, 1 BLOCKED, 2 input/tool error, 3 NEEDS_CONTEXT. Status reflects checked rules and supplied context, not an independent verification of every account setting. Bulk configuration readiness is separate from a performance analysis. Matching date labels alone do not reconcile Ads and Business Reports.

## PPC Bulk File QA

Copy the complete `skills/amazon-ppc-bulk-qa` folder to your agent's skill directory. Install `openpyxl` for reading/writing XLSX files.

Example request:

> Use amazon-ppc-bulk-qa to check these proposed Sponsored Products changes against this fresh bulk export. Preserve campaign names and IDs, limit new exacts to 25 per campaign, and prepare a checked upload plus a before/after list.

Run from the repository root:

```bash
python skills/amazon-ppc-bulk-qa/scripts/bulk_qa.py --manifest manifest.json --out output/bulk-qa-01
```

See [manifest and outputs](skills/amazon-ppc-bulk-qa/references/manifest-and-outputs.md) and [supported operations and primary sources](skills/amazon-ppc-bulk-qa/references/supported-operations.md). The manifest identifies one verified account, US/USD, UK/GBP or CA/CAD, snapshot timestamp/completeness, rules and any harvest links. Default policies: exact-only keyword creates, 25 new exacts per campaign, 25% bid/budget changes, a 48-hour configuration snapshot and 24-hour delivery evidence. These are configurable workflow limits, not Amazon-imposed limits.

V1 supports SP keyword creates/bid updates, campaign daily-budget updates and ad-group/campaign negative keyword creates. Unsupported products/operations and invalid rows prevent any upload. Checks include IDs and parents, exact names, duplicate exacts with same-ASIN scope, literal negative conflicts, protected terms/campaigns, finite amounts, freshness, formulas and Excel ID precision. Outputs include Markdown/JSON findings, exception and before/after CSVs, original-value audit JSON and a round-trip-verified checked XLSX when eligible.

Keyword harvesting uses two phases. A checked new exact can enter phase 1; its source negative stays out of that workbook. Phase 2 requires the destination's actual ID in a fresh read-back and recent keyword-level impressions, available budget and eligibility for every affected source ASIN. Evidence is user supplied, not fetched from Amazon. No API keys or live account changes are involved.

Exit codes: 0 READY/PHASE1_READY/NO_CHANGES, 2 BLOCKED or invalid input, 3 NEEDS_CONTEXT. A checked upload still requires human review and the current Amazon console/template's validation. Close variants and account-specific constraints remain review items.

## Video command-line use

Run from the repository root. Choose a new output directory for every invocation.

```bash
python skills/amazon-video-prep/scripts/amazon_video.py check input.mp4 --placement sb-video --out output/check-01
python skills/amazon-video-prep/scripts/amazon_video.py fix input.mp4 --placement sd-video --out output/export-01
python skills/amazon-video-prep/scripts/amazon_video.py check input.mp4 --placement listing-video --out output/listing-01
python skills/amazon-video-prep/scripts/amazon_video.py fix input.mp4 --placement sb-video --marketplace UK --content-language en-GB --out output/uk-01
python skills/amazon-video-prep/scripts/amazon_video.py check input.mp4 --placement sd-video --marketplace CA --content-language en-CA --out output/ca-01
```

`--marketplace US|UK|CA` selects the destination store, local source URLs, review locale and report labels. Omitted marketplace flags preserve the US default. `--content-language` records a supplied declaration, not detected or verified speech/text. UK and Canada add local English, product/ASIN, relevant currency/measurement and claims review. French-only/bilingual Canadian creative remains subject to actual placement/language verification. The script does not translate or create captions.

`fix` preserves content and duration by default, re-encodes to H.264 Main/MP4, normalizes frame rate and pixel shape, converts existing audio to AAC stereo/48 kHz, and rechecks the result. It refuses arbitrary truncation, automatic padding, unrequested cropping or upscaling, and automatic HDR conversion. For a reviewed excerpt/crop, explicitly provide `--start`, `--duration`, `--resize crop`, or `--allow-upscale` as appropriate.

The exporter copies ordinary container metadata. Required XMP/provenance labels, including applicable synthetic-performer disclosures in listing footage, must be verified/reapplied after export with a suitable tool; this is not certified by ffmpeg metadata copying.

Outputs include Markdown/JSON technical reports, a creative-review checklist, sampled frames and optional contact sheets, plus a corrected MP4 and export decisions when produced. The agent must fill the creative review from evidence; the script does not perform OCR, speech transcription or comprehensive claims analysis. Exit code 0 means no confirmed technical failures (review items may remain); 1 means technical failures; 2 means a tool/input/export error.

## Scope and source uncertainty

The rules snapshot was checked on 2026-10-13. UK/Canadian Sponsored Brands specifications match the shared horizontal profile. Display bitrate requirements conflict between official pages, so the skill discloses the disagreement and exports above both targets. Listing requirements need confirmation against the local Seller Central upload workflow: indexed shoppable guidance includes a 1–12 minute range, while older upload guidance lacks a duration limit. A provisional vertical Sponsored Brands Store profile is included. Listing videos are not subjected to the ad profiles' 45-second limit. See [marketplace review](skills/amazon-video-prep/references/marketplace-review.md) for sources and limits.

The shaded lower-right contact-sheet guide is an internal review aid, not Amazon's official template. Review the actual placement template before judging safe zones. Sparse frame samples cannot certify an entire video. Resizing low-resolution material does not restore detail.

## Tests

```bash
python -m unittest discover -s tests -v
```

Report preflight regression tests:

```bash
python -m unittest discover -s skills/amazon-report-preflight/scripts/tests -v
```

PPC Bulk File QA regression tests:

```bash
python -m unittest discover -s skills/amazon-ppc-bulk-qa/scripts/tests -v
```

The bulk QA suite contains 77 synthetic regression tests, including two-phase harvest gates, multi-ASIN coverage, duplicate/conflict checks, change caps and XLSX round-trip integrity. An independent agent also exercised a mixed proposal batch and a staged harvest batch. Real client-export and Amazon upload acceptance tests remain pending.

The report tests generate synthetic CSV/TSV/XLSX fixtures in temporary directories; openpyxl enables the XLSX cases. No client reports are bundled.

Tests generate synthetic media in a temporary directory; no client or copyrighted clips are bundled. Python, ffmpeg and ffprobe are required. Run the full suite after changing rules or encoding behavior.

## Contributing

Keep each skill under `skills/<name>/` with a concise `SKILL.md`, reusable scripts and source-backed references. Add meaningful regression tests for rule changes and file transformations. Do not commit client footage, transcripts, account details, credentials or generated outputs. Describe new dependencies and verify scripts on real media rather than only checking syntax.

MIT licensed; see [LICENSE](LICENSE).
