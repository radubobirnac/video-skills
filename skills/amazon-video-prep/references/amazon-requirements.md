# Placement requirements — US, UK and Canada

Snapshot checked 2026-10-13. Recheck before live submission preparation. Keep `profiles.json` aligned with evidence; do not substitute a generic "Amazon video" profile. Read [marketplace review](marketplace-review.md) for UK/Canadian source links, language and listing-workflow caveats. Localized UK/Canada Sponsored Brands specifications match the core horizontal profile; Display retains the documented source conflict.

## Sources

- [Sponsored Brands specifications](https://advertising.amazon.com/resources/ad-specs/sponsored-brands-video).
- [Video moderation guide](https://advertising.amazon.com/library/guides/sponsored-brands-display-ads-moderation).
- [Display video guide](https://advertising.amazon.com/library/guides/display-ads-video-creative).
- [Sponsored Brands API video specifications](https://advertising.amazon.com/API/docs/en-us/guides/sponsored-brands/ads/video).
- [Vertical Store campaign eligibility](https://advertising.amazon.com/resources/whats-new/sponsored-brands-video-introduces-vertical-video-creatives).
- [Seller Central upload help](https://sellercentral.amazon.com/help/hub/reference/external/GWJRQF3C34G4PRA2) and [shoppable video guide](https://sellercentral.amazon.com/help/hub/reference/external/GUZBYWTTVULY6C9Y).
- [Amazon staff's listing upload guidance](https://sellercentral.amazon.com/seller-forums/discussions/t/c31a136f-5f8d-4854-83c7-a7b88680d0c0).
- [Official horizontal Sponsored Brands safe-area template](https://m.media-amazon.com/images/G/01/AdProductsWebsite/images/AUX/SBv_safe_area_template_NEW.jpg).

## Checked rules and uncertainty

| Placement | Duration | Dimensions | Size | Notes |
| --- | --- | --- | --- | --- |
| Sponsored Brands horizontal | 6–45 s | 1280×720, 1920×1080, 3840×2160 | ≤500 MB | MP4/MOV; H.264/H.265; Main/Baseline; square pixels; progressive; listed frame rates |
| Sponsored Display horizontal | 6–45 s | At least 1920×1080; 16:9 | ≤500 MB | H.264, MPEG-2 or MPEG-4; 23.976, 24, 25 or 29.97 fps |
| Seller Central listing | No verified universal limit | Up to 1080p recommended | ≤5 GB, pending console confirmation | MP4/MOV; do not impose ad duration or aspect rules |
| Sponsored Brands Store vertical | Indexed API: 6–45 s | Indexed API: 720×1280, 1080×1920, 2160×3840 | Verify console | Eligible Store campaigns; full technical validation incomplete |

Horizontal SB audio can be absent. When present: AAC, MP3 or PCM; mono/stereo; at least 96 kbps and 44.1 kHz. A silent ad still needs review for whether it is obvious no one is speaking or whether a no-audio disclosure is needed. Do not add silent audio to satisfy a nonexistent requirement.

The Display moderation table uses 4 Mbps video and 192 kbps audio, while the Display creative guide uses 1 Mbps and 92 kbps. The latter labels both 6 and 45 seconds "Minimum duration". Use the moderation table for the 45-second maximum. Treat stricter bitrates as conservative review/export targets, not unquestionable rejection rules. MP4/MOV is an exporter preference for Display rather than a sourced exhaustive container list.

Seller help bodies were inaccessible without JavaScript/authentication. The 5 GB and format values have indexed current-help support and an older Amazon staff reply. Mark for live-console verification rather than claiming full current help access. Higher-than-1080p is a compatibility recommendation, not certain rejection.

The current indexed shoppable guide also lists a 1–12 minute range for that workflow. Do not assume the same duration rule applies to every listing upload flow without console verification. Each marketplace profile carries this uncertainty; no unverified duration limit is enforced automatically.

Use decimal MB/GB. Variable-frame-rate suspicion and missing bitrate metadata are review items. Encoded dimensions do not prove detail: do not call upscaled 360p footage high quality.

## Creative boundaries

Review current category-specific policies, suitability, product relevance, substantiation, marketplace language, text, bars, blank frames and jarring audio/cuts. The moderation guide flags reviews/star ratings, Amazon branding, savings promotions, urgent pressure and distracting effects in video ads. Do not automatically apply ad rules to listing videos or treat educational guides as a substitute for acceptance policies.

The horizontal SB page reserves the lower-right region for controls. The script's shaded lower-right guide (20% width ×25% height) is an internal conservative review aid, not the official template or a certified safe zone. Compare the actual placement against the official template; vertical/Display/listing layouts may differ.
