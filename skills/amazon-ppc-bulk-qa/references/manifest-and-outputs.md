# Manifest and outputs

## Context and rules

Supply a JSON manifest. Resolve input paths relative to that manifest. Use exact worksheet names if several worksheets contain SP entity rows. CSV uses commas, TSV uses tabs; headers must be on the first row. Preserve original headers and values in the audit. Files must use one verified account/profile and marketplace; a file without account columns cannot independently prove its account identity.

```json
{
  "snapshot": "fresh-bulk.xlsx",
  "snapshot_sheet": "Sponsored Products Campaigns",
  "changes": "proposals.csv",
  "account_id": "verified-profile-id",
  "marketplace": "UK",
  "currency": "GBP",
  "snapshot_exported_at": "2026-10-14T08:00:00Z",
  "reviewed_at": "2026-10-14T10:00:00Z",
  "snapshot_complete": true,
  "rules": {
    "new_exact_only": true,
    "max_new_exacts_per_campaign": 25,
    "max_bid_change_pct": 25,
    "max_budget_change_pct": 25,
    "snapshot_max_age_hours": 48,
    "delivery_max_age_hours": 24,
    "duplicate_scope": "same_asin",
    "protected_terms": ["acme widget"],
    "protected_campaign_ids": ["123456789"]
  }
}
```

Use US/USD, UK/GBP or CA/CAD. Supply ISO timestamps with UTC offsets. `reviewed_at` defaults to the execution time; an explicit timestamp represents an as-of review and must be described that way. Do not manufacture `snapshot_complete: true`: verify the download includes all relevant entity types, paused records and records without performance. Campaigns/ad groups must exist, and IDs must resolve to the correct parents. A row's Account ID, Profile ID, Marketplace or Currency, when present in the snapshot, must agree with the manifest.

All numeric rules must be positive decimal numbers except the new-exact cap, which is a nonnegative integer. Optional `max_new_bid` and `max_daily_budget` set currency-specific absolute ceilings. Unknown rules fail validation. `new_exact_only: false` permits broad/phrase creates; the 25 cap and cross-scope duplicate checks apply to exact creates. All amounts use unformatted dot decimals; percentages measure absolute change from the snapshot. An unchanged update is rejected.

`duplicate_scope` accepts `same_asin` (default), `campaign` or `ad_group`. Same-ASIN checks block enabled or paused existing exacts for overlapping products across campaigns; unrelated products may use the same term. Missing ASIN mappings prevent certification of that check. Archived exacts receive warnings. Normalize NFC, case and whitespace for comparison; preserve actual text and names in audit/output. Do not assume fuzzy duplicates or close variants are equivalent.

## Harvest links

Row numbers refer to physical proposal-file rows, counting the header as row 1. Link source Negative Exact creates only. Each negative needs a unique link with exactly one destination selector.

Phase 1:

```json
"harvest_links": [{"negative_row": 3, "positive_row": 2}]
```

The positive must pass QA, target an existing manual campaign/ad group and cover every source ASIN. Exclude the linked source negative from this upload. A negative that would block its own destination fails. The new exact's ID is obtained from the subsequent Amazon read-back, never guessed.

Phase 2, after upload processing and delivery:

```json
"harvest_links": [{
  "negative_row": 2,
  "destination_keyword_id": "987654321",
  "delivery_evidence": {
    "checked_at": "2026-10-14T09:00:00Z",
    "window_start": "2026-10-14T00:00:00Z",
    "window_end": "2026-10-14T08:00:00Z",
    "keyword_id": "987654321",
    "impressions": 20,
    "budget_available": true,
    "eligible_asins": ["B000000001"],
    "reference": "Keyword-level report filename/rows plus console eligibility and budget check"
  }
}]
```

The keyword must be present in the fresh snapshot, enabled, exact and match the source term. Its campaign/ad group and product ads must be enabled, campaign dates current, daily budget positive, and no existing/proposed negative may block it. The destination and evidence must cover **all** affected ASINs, including all source-campaign products for campaign-level negatives. Evidence needs positive integer impressions during a window entirely within the configured recent period, available budget and an identifiable reference. Evidence is user supplied, not independently fetched or authenticated. Obtain it from actual reports/console checks; do not substitute general campaign impressions or all-time totals.

An unlinked negative exact matching another same-product exact is treated as potential routing and needs context. A waste-removal negative without such a destination can pass ordinary conflict/protection checks. Brand and launch protection is explicit through configured IDs/terms; campaign names alone are not a reliable protection policy. Phrase/broad keyword overlap receives a warning; direct exact conflicts block. Manually review close variants and traffic effects.

## Files and statuses

| File | Purpose |
| --- | --- |
| `report.md`, `report.json` | Overall status, context, limits, all row issues and proposed payloads |
| `exceptions.csv` | Row-specific failures, deferred reasons and warnings |
| `changes.csv` | IDs, original campaign name, field-level before/after and row status |
| `deferred.csv` | Source-negative proposals held for phase 2; never upload directly |
| `audit.json` | Original snapshot/proposals, physical rows, headers, manifest and SHA-256 hashes |
| `checked-upload.xlsx` | READY rows only, minimal supported mutation fields, IDs stored as literal text |

If any global/row failure is BLOCKED or NEEDS_CONTEXT, create reports but no upload. PHASE1_READY permits an upload of READY rows with deferred negatives excluded. No arbitrary partial file is produced when another row fails. Rerun deliberately revised proposals into a new directory; existing output directories are refused.

Exit codes: 0 = READY, PHASE1_READY or NO_CHANGES; 2 = BLOCKED or invalid input; 3 = NEEDS_CONTEXT. Invalid unreadable/schema/formula input fails before report creation and prints a specific error. Missing `openpyxl` can prevent reading XLSX or creating an upload. A failed upload export changes the report to BLOCKED.

The workbook is round-trip verified with literal string cells and no formulas. Audit CSVs escape formula-like cell prefixes; raw values remain in JSON. Preserve source files and compare hashes. Do not claim an upload was accepted: the current Amazon template/console may require additional fields or impose marketplace/account-specific limits.
