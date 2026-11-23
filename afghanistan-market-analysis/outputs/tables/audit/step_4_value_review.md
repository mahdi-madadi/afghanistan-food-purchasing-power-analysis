# Step 4: Source definitions and value screening

## Verified source definitions

HDX HAPI defines actual as prices collected monthly and aggregate as prices collected daily or weekly and converted to monthly values using a weighted mean. The combined actual,aggregate entry has no explanatory text in this table.

Source: https://hdx-hapi.readthedocs.io/en/latest/data_usage_guides/enums/#price-flag (accessed 15 November 2026).

The HDX price guide treats dates represented by the 15th as monthly reference periods, rather than evidence of a survey conducted on that exact day.

Source: https://hdx-hapi.readthedocs.io/en/latest/data_usage_guides/food_security_nutrition_and_poverty/#transformations-applied_1 (accessed 15 November 2026; see Food Prices & Market Monitor).

All selected wage and low-quality flour observations for May 2020–December 2025 are flagged aggregate. Retain these monthly observations and preserve the flag. This flag alone is not evidence of spatial aggregation or duplicated national totals. Exact within-month weights and original daily/weekly observations are not supplied in our CSV.

## Value screen

| Series | Rows | Minimum | Median across records | Maximum |
|---|---:|---:|---:|---:|
| Low-quality wheat flour, AFN/kg | 2,312 | 19.90 | 31.51 | 59.25 |
| Unskilled non-agricultural wage, AFN/day | 2,311 | 150.00 | 300.00 | 600.00 |

These are unweighted pooled descriptive values, not national estimates. Both series cover 34 market IDs; the wage series has one missing market-month. Ranges alone do not validate the observations.

The script flags absolute month-on-month changes of at least 25%, calculated only for consecutive calendar months within the same market and commodity. This analyst-selected screening threshold is not a WFP error rule or a statistical significance test. It flags 46 changes for review. No records have been corrected or removed.

Largest flagged change: Bamyan wages rose from AFN 200/day in April 2023 to AFN 350/day in May 2023, a 75% increase. This is an observed change requiring investigation, not a confirmed error or an explained economic event.

## Your Excel exercise

1. Import large_monthly_changes_review.csv from outputs/tables/audit into a new worksheet called Value_Review.
2. Review the first five entries, already sorted by absolute change.
3. Add a calculated column named recalculated_change_percent. With an Excel Table, use =100*([@price]/[@previous_price]-1). Format as a number with two decimals, not Excel percentage format, because the formula already multiplies by 100.
4. Confirm the first entry is 75.00. Alternatively use =[@price]/[@previous_price]-1 and format as Percentage; do not combine multiplication by 100 with percentage formatting.
5. For Bamyan, filter the raw-data worksheet by market_id 268, the exact unskilled-wage commodity, and dates March–July 2023. Examine whether the change persists or reverses. This can guide investigation but does not prove its cause.
6. In review_note, describe the observed pattern. Use review_status values such as Unreviewed, Checked against raw CSV, or Needs external verification. Matching the raw CSV verifies transcription only, not economic accuracy.
7. Save the XLSX; leave original CSVs untouched. Document any later correction with its evidence and original value.

## Next analytical stage

After reviewing the flagged changes, build a 34-market × 68-month table with separate wage and flour columns and retained source flags. Keep Daykundi February 2025's wage and purchasing-power ratio missing. Divide wage AFN/day by flour AFN/kg to obtain kg per paid workday. This is the ratio of reported monthly series, not the average of daily purchasing-power ratios, employment availability, or actual household consumption.

Reproducibility: src/03_review_values.py uses Python's standard library, reads only the price CSV, and produces selected_value_summary.csv, large_monthly_changes_review.csv, and selected_extreme_values.csv in outputs/tables/audit. Screening is limited to these two series and the candidate study period.
