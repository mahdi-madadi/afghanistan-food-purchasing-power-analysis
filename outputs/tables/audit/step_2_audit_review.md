# Step 2: Review of Excel pivots and initial data audit

The saved commodity-by-unit pivot (Sheet3, A3:G21) and price-flag pivot (Sheet4, A3:B7) were independently compared with the raw CSV. Every commodity/unit count, all three flag counts, and both grand totals match. This checks saved values, not live Excel refresh behavior. The workbook and raw files were not changed.

## Findings

| Check | Result |
|---|---:|
| Price records | 45,737 |
| Blank fields in original CSV columns | 0 |
| Invalid dates | 0 |
| Missing or nonnumeric prices | 0 |
| Nonpositive prices | 0 |
| Exact duplicate rows beyond first occurrence | 0 |
| Rows with duplicate observation keys | 0 |
| Unique market IDs in price file | 40 |
| Unique market IDs in lookup | 140 |
| Price-market IDs absent from lookup | 0 |
| Retail records | 45,737 |
| Records flagged actual | 8,760 |
| Records flagged actual,aggregate | 472 |
| Records flagged aggregate | 36,505 |

The observation key checked is date + market_id + commodity_id + unit + pricetype + currency. Absence of duplicates under this key does not establish the meaning or spatial level of aggregate records.

Cooking oil is recorded in KG. Preserve that unit and do not relabel its prices as per liter.

## Proposed-period feasibility

Window assessed: January 2019–December 2025, or 84 calendar months. Matching requires AFN, Retail, positive prices, wages in Day, flour in KG, and exactly one record per market/month for each component. Each flour quality is assessed separately. All price flags are retained for the primary feasibility check, not yet approved as equivalent observations.

| Flour series | Matched market-months | Markets with matches | Markets with all 84 months |
|---|---:|---:|---:|
| Wheat flour | 24 | 4 | 0 |
| Wheat flour (high quality) | 2,311 | 34 | 0 |
| Wheat flour (low quality) | 2,311 | 34 | 0 |

For low-quality flour, 33 markets have 68 matching months (80.95%); Daykundi has 67 (79.76%). Identical counts do not prove the missing months are identical. An actual-only filter leaves no matched high- or low-quality flour observations in this window. Do not discard aggregate flags without checking source definitions.

No blank cells does not mean complete time coverage: a missing market/month can be absent as a whole row.

## Your next exercise in Excel

1. Optionally rename Sheet3 to Commodity_Units, Sheet4 to Price_Flags, and Sheet2 to Raw_Import. These are suggestions; the workbook has not been edited. The current audit script checks the existing sheet names, so update its references if you rename them.
2. Import wage_flour_coverage_2019_2025.csv from the audit folder through Data > From Text/CSV into a new worksheet.
3. Filter flag_policy to all_flags and flour to Wheat flour (low quality).
4. Filter matched_months to greater than zero and sort it ascending.
5. Check that Daykundi shows 67, the other 33 markets show 68, and the total is 2,311.
6. Write a short interpretation: what is the denominator of 84, why are absent rows different from blank cells, and why does the aggregate flag require investigation?

Next analytical stage: inspect the exact missing months and the time pattern of price flags; confirm WFP aggregation methodology; then choose a defensible period and inclusion rule. Do not impute gaps or pool flour qualities yet.

## Reproducing the audit

The project now contains src/01_audit_data.py. It uses pandas for analysis and openpyxl only to read saved workbook values. It never writes to the Excel workbook or raw CSVs. It saves descriptive CSV tables and an audit_summary.json containing source SHA-256 hashes to outputs/tables/audit.

With Python, pandas, and openpyxl available, run from the project root:

```powershell
python src/01_audit_data.py
```

The ordinary python command was not available in this session, so execution used the bundled Python runtime. No software was installed and no system settings were changed. The script ran successfully. Its workbook checks refer to the current Sheet3 and Sheet4 layout.

This is an initial structural and coverage audit. It does not yet validate extreme values, historical currency consistency, geographic interpretation, source methodology, or economic conclusions.
