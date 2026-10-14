# Source notes

Checked 2026-10-13. These are reporting interpretation sources, not a guarantee that every current Amazon export format is supported. Some Seller Central pages require a signed-in account; indexed official definitions were available. Verify the actual report settings for unfamiliar formats.

| Source | What it supports |
| --- | --- |
| [Amazon Ads: Ad campaign attribution](https://advertising.amazon.com/help/GX7KDKHMWQYMJ385) | Campaign sales use ad interaction dates; conversion settings can differ from retail reporting. |
| [Amazon Ads: SP search-term report](https://advertising.amazon.com/help/G3HEFZYWZF84NPS9) | Query reports include clicked terms, so impressions need not match campaign totals. |
| [Amazon Ads: SB search-term report](https://advertising.amazon.com/help/GLPHMX59DC5WSSQW) | Clicked-query coverage and the limit on impression reconciliation. |
| [Amazon Ads: reports for book advertising](https://advertising.amazon.com/en-us/library/guides/book-advertising-reporting) | Campaign, targeting, search-term and advertised-product reports describe distinct report coverage/grains. Book-specific examples do not establish every seller's attribution settings. |
| [Seller Central: Business reports glossary](https://sellercentral.amazon.com/help/hub/reference/external/G27691) | Ordered sales, units, order items and sessions retain their own meanings. |
| [Seller Central: Product Performance Spotlight glossary](https://sellercentral.amazon.com/gp/help/external/G5T9UKA4NXTH7G4S) | One order can have multiple order items and each order item multiple units. |
| [Amazon Ads API: Ads performance dataset](https://advertising.amazon.com/API/docs/en-us/guides/amazon-marketing-stream/v2/datasets/ads-performance) | Reporting schemas evolve and consolidate formats. API streams are not directly parsed by this export-only release. |
| [openpyxl: loading workbooks](https://openpyxl.readthedocs.io/en/stable/api/openpyxl.reader.excel.html) | read_only, data_only and keep_links behavior. This reader uses data_only=False and never evaluates formulas. |

Implementation policy: require explicit report context, use exact decimal arithmetic, preserve row lineage, keep incomplete reports out of ready totals, and avoid inferred sales reconciliations. These conservative choices are our workflow design, not claims that Amazon requires this manifest or status model.
