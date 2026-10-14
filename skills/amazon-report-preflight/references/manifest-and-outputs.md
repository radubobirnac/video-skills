# Manifest and output contract

## Example manifest

Paths are relative to the manifest directory or absolute. Use one entry per worksheet when report context differs. Scope describes the filters, product coverage and campaign coverage actually exported. The values below illustrate a historical, settled Sponsored Products export; replace them with evidence for the supplied report.

```json
{
  "version": 1,
  "as_of": "2026-10-13",
  "required_reports": ["search_term"],
  "reports": [{
    "id": "sp-search-terms",
    "path": "search-terms.csv",
    "type": "search_term",
    "account": "seller-profile-identifier",
    "marketplace": "US",
    "currency": "USD",
    "timezone": "America/Los_Angeles",
    "start_date": "2026-09-01",
    "end_date": "2026-09-30",
    "aggregation": "summary",
    "scope": "all SP campaigns; all advertised products; no campaign filter",
    "ad_type": "SP",
    "date_basis": "ad_interaction",
    "attribution_days": 7,
    "attribution_model": "click",
    "sales_scope": "total",
    "number_locale": "dot",
    "date_format": "iso"
  }]
}
```

Do not copy this timezone or conversion window into another account without verification. A number in a mapped conversion metric header can establish its window; it must match an explicitly declared window. Headings such as sales7d/purchases14d are also recognized.

## Report fields

| Field | Meaning |
| --- | --- |
| id, path | Unique simple ID; source path. |
| type | auto, campaign, search_term, targeting, advertised_product, business, bulk. |
| sheet | Exact XLSX worksheet name. Without it, all nonempty worksheets are inspected separately. |
| header_row | Explicit positive physical header row. Otherwise inspect the first 50 rows for recognized English headers. |
| account | Account/profile identity from supplied context, not a guessed brand name. Use consistent identity across compared reports. |
| marketplace, currency | US/USD, UK/GBP, CA/CAD. File evidence can establish market/currency; $ alone cannot distinguish US and Canada. |
| timezone | Actual report timezone as an IANA name. User location does not establish it. |
| start_date, end_date | Confirmed requested export period, inclusive, ISO dates. Observed daily rows do not establish the full requested range. |
| aggregation | daily or summary. Daily needs Date. Summary with a daily Date column needs review. |
| scope | Explicit nonempty description of filters/product/campaign coverage. Matching labels depend on the supplied declaration. |
| ad_type | SP, SB or SD, for performance exports. Use separate entries for different ad products. |
| date_basis | ad_interaction, order, conversion. Confirm the selected report definition. |
| attribution_days | Integer 1–90. Header windows can fill this when unambiguous. |
| attribution_model | click or click_and_view. The script does not infer this from sales counts. |
| sales_scope | total, advertised_sku or other_sku. Default aliases map Total Sales, not advertised/halo submetrics. Explicit alternate metrics need column_map. |
| number_locale | dot (default; 1,234.56) or comma (1.234,56 / 1 234,56). Locale applies only to numeric cells, not query text. |
| date_format | iso (default), mdy or dmy for source date cells. Manifest periods always use ISO. |
| encoding | utf-8-sig (default), utf-8, utf-16, cp1252. Declare a non-UTF8 source explicitly. |
| delimiter | comma, tab or semicolon as a one-character string. Otherwise CSV is detected, TSV uses tab. |
| column_map | Object mapping canonical fields to exact source header strings. Resolve ambiguities explicitly; never map one column twice. |
| exclude_rows | Confirmed physical source row numbers to exclude, for example an inspected grand total. Each exclusion retains raw values in the decision log. |
| confirmed_data_rows | Physical rows explicitly confirmed as real data when a name such as Total triggers summary-row review. These rows cannot also be excluded. |

Business Reports require account, market/currency, timezone, period, aggregation, date basis and scope. Their order_items are retained as order items, not renamed to customer orders. Bulk entity sheets require account, market and currency for structural readiness; they produce no performance totals. A bulk configuration snapshot is not proof of historical configuration freshness.

Recognized canonical fields are declared in the script's ALIASES dictionary. Explicit column_map supports localized headers but does not certify the correctness of a semantic mapping. Unknown columns remain in the raw audit data. Counts/amounts are exact decimal strings in JSON/CSV, not binary floats. Negative amounts and credit/settlement files are outside these performance profiles.

## Outputs

| File | Use |
| --- | --- |
| report.md | Human findings, status and limits. |
| report.json | Full context, source SHA256, original cell text, column mappings, findings, recorded decisions and exact per-report totals when READY. |
| exceptions.csv | Report and batch errors, context requests and warnings with physical row/field references. |
| normalized-audit.csv | All retained rows, including blocked/context-incomplete/excluded-duplicate rows; original values and unknown columns in raw_json. |
| analysis-ready.csv | Only nonexcluded rows of individually READY reports. Preserve report boundaries; this is not a merged additive fact table. |
| comparisons.json | Pairwise compatibility checks and diagnostic Ads differences where context aligns. No organic-sales subtraction. |
| joins.json | Unique current bulk ASIN mapping and Business Report coverage counts. No sales allocations. |
| manifest-draft.json | First-inspection manifest, emitted only in file-list mode. Add confirmed context before using it for downstream analysis. |

All values that could execute as CSV formulas are escaped with a leading apostrophe; original values remain in raw_json/report.json. Exact deduplication compares full raw cells in one file/sheet. Same query at different dates, match types or ad groups is not a duplicate. Repeated file content/sheets supplied twice are blocked on the second occurrence.

The script refuses an existing output directory, never modifies source files, and reads no credentials. Input limit: 100 MiB per file, 250,000 rows, 500 columns, 512 MiB expanded XLSX content. Blocked reports contribute no partial totals. Sources with spreadsheet formula cells in mapped fields need a values-only re-export. XLSX export and macros are unsupported.
