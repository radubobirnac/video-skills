# Supported operations and source notes

## Operation contract

Use `Product = Sponsored Products`. Product, Entity and Operation comparisons ignore case/outer whitespace; output uses canonical labels. IDs must be original numeric strings, with leading zeros retained. Current exports are the authority for IDs, parent relationships and names. Never use campaign-name placeholders to target existing entities.

| Entity / Operation | Required proposal values | Scope |
| --- | --- | --- |
| Keyword / Create | Campaign ID, Ad Group ID, Keyword Text, Match Type, Bid, State enabled; Keyword ID empty | Existing enabled manual campaign/ad group with enabled product ads |
| Keyword / Update | Campaign ID, Ad Group ID, Keyword ID, Bid | Bid only; referenced keyword must belong to both parents |
| Campaign / Update | Campaign ID, Daily Budget; Ad Group ID empty | Budget only |
| Negative Keyword / Create | Campaign ID, Ad Group ID, Keyword Text, Negative Exact/Phrase, State enabled; Keyword ID and Bid empty | Ad group |
| Campaign Negative Keyword / Create | Campaign ID, Keyword Text, Negative Exact/Phrase, State enabled; Ad Group ID, Keyword ID and Bid empty | Campaign |

Accept optional Campaign Name and Ad Group Name solely to check exact equality with the snapshot. Recognize their `(Informational only)` header aliases. Omit names from the upload to avoid accidental renames. Reject duplicate aliases rather than guess which column is authoritative. Updates may contain unchanged fields from their original entity: compare them with the snapshot and record their omission. Reject changed/unverifiable extras. Creates reject nonempty fields outside the contract. Do not silently discard unknown nonempty columns.

Emit these upload columns: Product, Entity, Operation, Campaign ID, Ad Group ID, Keyword ID, State, Daily Budget, Bid, Keyword Text, Match Type. Populate only fields permitted for each operation. Empty fields represent omitted edits; updates do not set State. Review a current account template before upload. A checked workbook is not a guarantee of Amazon acceptance.

Do not support SB/SD/DSP, campaign/ad-group/product-ad creation, portfolio changes, placements, bidding strategy, product targeting, renames, state changes or archives in v1. Do not treat a lack of support as a policy prohibition by Amazon; extend and test separately.

## Current primary references

Research snapshot: 2026-10-14. Amazon's public API documentation is a JavaScript application, and some help pages require account context. Public indexed excerpts were available for the items below. Confirm current field details in the account's own exported template; the checker deliberately uses a narrow operation set.

- [Manage campaigns with bulksheets](https://advertising.amazon.com/help/GPVTCZRJ7G9HXHWB): entity-row model.
- [SP bulksheets getting started](https://advertising.amazon.com/API/docs/en-us/no-code-tools/bulksheets/sp/get-started) and [create examples](https://advertising.amazon.com/API/docs/en-us/no-code-tools/bulksheets/sp/sp-examples/create-sp-campaign): Product, Entity, Operation and entity IDs.
- [Update SP campaigns](https://advertising.amazon.com/API/docs/en-us/no-code-tools/bulksheets/sp/sp-examples/update-sp-campaigns): supported platform operations extend beyond this skill's narrow v1.
- [Bulk error reports](https://advertising.amazon.com/API/docs/en-us/bulksheets/2-0/bulksheets-error-reports) and [migration guide](https://advertising.amazon.com/API/docs/en-us/no-code-tools/bulksheets/migration-guide): use original individual entity IDs and review processing errors.
- [Negative keyword rules](https://advertising.amazon.com/help/GTEHPEG5BXY9UX5W): negative exact up to 10 words/80 characters, negative phrase up to 4 words/80 characters; no broad negative. Processing/delivery effects can be delayed.
- [Sponsored Products targeting guide](https://advertising.amazon.com/library/guides/targeting-with-sponsored-products): positive keyword length up to 10 words/80 characters and documented unsupported punctuation; keywords apply to products within their ad group.
- [Keyword match types](https://advertising.amazon.com/help/GHTRFDZRJPW6764R): exact can include close variants; existing match type cannot simply be edited into a different match type.
- [Campaign limits](https://advertising.amazon.com/help/G86H2227323T8T4Q): platform capacity may vary/increase. Do not present the 25-new-exact workflow cap, 25% change ceilings, 48/24-hour evidence policies or same-ASIN duplication policy as Amazon-imposed limits.

Scope differences and current Amazon account validation remain external review items. No code here measures profitability or uses live API credentials.
