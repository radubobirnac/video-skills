# Report profiles and semantics

| Profile | Minimum mapped fields | Grain and important distinctions |
| --- | --- | --- |
| campaign | Campaign ID or name; clicks, spend, purchases/orders, attributed sales | Daily or period campaign performance. Preserve ad product, filters and conversion definitions. |
| search_term | Campaign ID/name, customer search term, clicks, spend, purchases/orders, sales | Query within targeting/ad-group/date context. Keep rows from different match types and destinations distinct. Search-term impressions do not cover all campaign impressions. |
| targeting | Campaign ID/name; target text or keyword/target ID; clicks, spend, purchases/orders, sales | Keyword or product-target performance. Do not join solely by keyword text or mix query and target grains. |
| advertised_product | Campaign ID/name; advertised ASIN or SKU; clicks, spend, purchases/orders, sales | Advertised-product grain. Total attributed sales can include other products; this is not a purchased-product report. |
| business | Child ASIN or SKU; Ordered Product Sales | Retain parent separately. Sessions, Units Ordered and Total Order Items are optional distinct metrics. Parent-only exports need another profile and are blocked rather than allocated to children. |
| bulk | Entity; Campaign ID/name | Configuration/entity sheets, not an additive performance fact table. IDs stay text. Mixed entity metrics are not summed. Separate search-term worksheets are classified as search_term in auto mode. |

Automatic recognition covers common English CSV and Ads API-style camelCase headers. Unrecognized/localized variants require explicit header_row, type and column_map. Unsupported or ambiguous columns are reported, never guessed. Core performance profiles need both attributed purchases/orders and sales; partial traffic reports remain blocked for this complete analysis profile.

Normalize zeroes as zeroes. Leave optional blank metrics unavailable. Do not assume orders cannot exceed clicks: repeat purchases and view attribution can affect those relationships. Units Ordered and Total Order Items are different counts. B2B columns are subsets; retain them as unmapped source data rather than adding them to totals.

Do not assume matching date labels establish identical sales:

- Sponsored ad campaign sales are assigned to the interaction date according to the selected attribution settings. Retail ordered sales describe a different measure.
- Conversion windows and click/view models vary by format, account and report. Infer only named header windows, and obtain the remaining settings from evidence.
- A full attribution window is a minimum waiting condition. Adjustments can continue after it. The script marks periods ending within that minimum window NEEDS_CONTEXT.
- Campaign, target and query totals may differ because reporting coverage, filters and grain differ. Pairwise differences are diagnostics, not exact reconciliations.

Preserve raw account/profile, marketplace, filters, date range, timezone, column meanings and each source's row grain. Keep separate files for separate ad products/marketplaces. New global/unified formats may require explicit mappings or a future profile; do not force their fields into older meanings.

ASIN joins use account + marketplace + campaign ID + ad-group ID. Resolve a current configuration only when the bulk product-ad group contains one ASIN. Do not match by campaign names, allocate mixed-ASIN performance, infer purchased products or prove that an ASIN was advertised throughout the historical period. Missing Business Report rows can reflect export scope or no activity and do not prove a catalog defect or out-of-stock event.
