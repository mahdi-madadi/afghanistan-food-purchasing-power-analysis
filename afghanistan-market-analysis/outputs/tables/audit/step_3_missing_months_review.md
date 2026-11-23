# Step 3: Exact missing months

## Finding

For unskilled non-agricultural wages in AFN/Day and low-quality wheat flour in AFN/KG, the 34-market cohort has no matched observations from January 2019 through April 2020. During these 16 months, three markets have wage observations without matching flour observations; the other 31 have neither eligible series. This describes availability in this file, not the absence of market activity.

From May 2020 through December 2025, there are 2,311 matched market-month observations out of 2,312 possible (34 markets × 68 months), or 99.96%. The sole unmatched pair is Daykundi (market_id 3692), February 2025. It has an eligible low-quality flour price but no eligible unskilled wage observation.

Eligibility: Retail, AFN, positive price, the exact commodity labels and units above, and exactly one record per market/month/component. All price flags are included provisionally. No multiple-record ambiguity was found in this matching grid. These results do not establish what aggregate flags represent or whether the geographic units are comparable.

## Candidate study design

- Period: May 2020–December 2025.
- Geography: the 34 market IDs with matched observations. Do not describe them as representative province samples without checking source documentation.
- Primary food: low-quality wheat flour.
- Wage: Wage (non-qualified labour, non-agricultural).
- Indicator, after validation: daily wage divided by flour price, in kg per paid workday.
- Missing observation: leave Daykundi February 2025 unavailable. Do not substitute zero or forward-fill a wage.
- Summary handling: report 33 contributing markets for February 2025 and 34 otherwise. Compare the main results against a fixed 33-market panel excluding Daykundi as a sensitivity check.
- Treat 2026 separately from this proposed complete-year end date. This is a study-design choice, not a claim that 2026 observations are invalid.

This is a candidate design. Validate aggregation flags, geographic interpretation, and value plausibility before freezing the research dataset.

## Excel exercise

1. Import monthly_coverage_summary.csv from the project's outputs/tables/audit folder into the existing workbook using Data > From Text/CSV.
2. Name the new worksheet Monthly_Coverage.
3. Filter matched to values below 34. You should see 17 rows: 16 months with zero matches and February 2025 with 33 matches.
4. Import missing_months_2019_2025.csv into a separate worksheet named Missing_Months.
5. Filter market to Daykundi and month to 2025-02. Confirm status is wage_missing, wage_rows is 0, and flour_rows is 1.
6. Save the XLSX. Keep the source and audit CSV files unchanged.

Record this methodological note:

> The candidate analysis period is May 2020–December 2025, based on joint availability of unskilled-wage and low-quality wheat-flour observations. It contains 2,311 of 2,312 possible market-month pairs across 34 market IDs. The missing Daykundi wage observation in February 2025 is retained as missing. Inclusion of aggregate-flagged records remains subject to validation of source definitions.

## Reproducibility

The project script src/02_check_missing_months.py creates the full 34 × 84 market-month grid for 2019–2025, identifies each absent component, and writes the coverage tables. It does not modify the raw CSVs or workbook. Its optional saved-workbook inspection uses openpyxl without saving changes. The cohort is conditional on at least one matched observation in 2019–2025; it is not all 40 market IDs in the price file.
