# US, UK and Canada marketplace review

Checked 2026-10-13. The script selects country-specific sources and reports using `--marketplace US|UK|CA`; omitted flags retain the US default. Technical placement profiles are shared only where verified specifications match. Keep country overrides in `profiles.json` if future differences appear.

| Marketplace | Store | Default review locale | Creative review |
| --- | --- | --- | --- |
| US | amazon.com | en-US | US product/ASIN, language, landing-page claims and local presentation |
| UK | amazon.co.uk | en-GB | British English, UK product/ASIN, relevant GBP prices and appropriate local measurements |
| Canada | amazon.ca | en-CA | Canadian English, Canadian product/ASIN, relevant CAD prices and local measurements; verify any French/bilingual target |

Spelling, currency and measurement suggestions are localization review items, not blanket technical rejection rules. Do not insert prices into ads when the placement's policy disallows that message. Do not change a brand's spelling, registered name, product label or claim without context. Same-looking products can have different ASINs, availability or permissible claims across stores.

## Primary sources

UK:
- [Sponsored Brands](https://advertising.amazon.com/en-gb/resources/ad-specs/sponsored-brands-video).
- [Display](https://advertising.amazon.com/en-gb/library/guides/display-ads-video-creative).
- [Moderation](https://advertising.amazon.com/en-gb/library/guides/sponsored-brands-display-ads-moderation).
- [Seller Central upload](https://sellercentral.amazon.co.uk/help/hub/reference/external/GWJRQF3C34G4PRA2) and [shoppable guide](https://sellercentral.amazon.co.uk/help/hub/reference/external/GUZBYWTTVULY6C9Y).

Canada:
- [Sponsored Brands](https://advertising.amazon.com/en-ca/resources/ad-specs/sponsored-brands-video).
- [Display](https://advertising.amazon.com/en-ca/library/guides/display-ads-video-creative).
- [Moderation](https://advertising.amazon.com/en-ca/library/guides/sponsored-brands-display-ads-moderation).
- [Seller Central upload](https://sellercentral.amazon.ca/help/hub/reference/external/GWJRQF3C34G4PRA2) and [shoppable guide](https://sellercentral.amazon.ca/help/hub/reference/external/GUZBYWTTVULY6C9Y).
- [Canadian Amazon staff reply on 5 GB/up-to-1080p](https://sellercentral.amazon.ca/seller-forums/discussions/t/0b1ed579-e4c2-4022-8dda-3f5e8ddd3fb0).

## Language evidence and limits

[Amazon's supported-primary-language page](https://advertising.amazon.com/help/GR6WPLZ2UUJMXCH8) is indexed as English for US, UK and Canada. Its full body was not publicly readable at verification. The localized Sponsored Brands pages and moderation guides require matching the marketplace's primary language, with translated subtitles/on-screen explanation when appropriate.

Use English advertising defaults. Treat French-only or bilingual Canadian creative as requiring current campaign/placement confirmation, rather than automatic rejection or automatic acceptance. Listing-content language and any region/category-specific requirements need their own review. Do not assert nationwide compulsory bilingual video, give legal approval, or substitute a guessed language rule.

`--content-language en-GB`, `en-CA`, or `fr-CA` records supplied information; it never detects language. Review transcripts, visible text and subtitles using available tools. The script does not translate, rewrite, render new captions or automatically validate language. Preserve brand names and intended meaning during any later translation work.

## Listing workflow uncertainty

Current local Seller Central help bodies require authentication/JavaScript. Canada has a local staff reply supporting 5 GB and up-to-1080p, while the UK fallback remains the older US staff guidance. Indexed current shoppable-guide text also mentions a 1–12 minute duration range and horizontal/vertical aspect ratios. Confirm the actual upload workflow before applying those limits; do not silently turn all listing clips into minute-long videos or impose the ad 45-second maximum. The listing profile remains provisional.

## Required provenance metadata

[Amazon's News announcement](https://sellercentral.amazon.co.uk/seller-forums/discussions/t/0e162209-1955-4708-9043-6a1530ab8f6e) says listing/A+ media containing photorealistic AI-generated people requires a synthetic-performer keyword in XMP dc:subject across worldwide stores. Check the linked tagging instructions and the current applicable policy when relevant. The exporter copies ordinary container metadata rather than removing it, but ffmpeg copying does not certify preservation of XMP or correctness of the disclosure. Verify/reapply the required label with an IPTC-compatible editor after export when applicable. The script neither detects synthetic people nor adds certified XMP labels.

Real-ad validation is pending. Initial implementation tests use generated fixtures, verify country routing and output, and make no claim that natural-language or creative judgment has been validated on client ads.
