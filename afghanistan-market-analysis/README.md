# Afghanistan Food Prices and Wage Purchasing Power

## Project overview

This project examines the amount of low-quality wheat flour purchasable with one reported paid day of unskilled work in monitored Afghan markets. It uses monthly market data from May 2020 to December 2025 to describe changes in food affordability across 34 monitored markets.

The project combines Excel data review, Power BI reporting, Python validation, a research paper, and a professional presentation. It is designed as a portfolio project for data-analysis, research, and humanitarian-monitoring roles.

## Research question

How did reported daily wages and low-quality wheat flour prices change the purchasing power of one paid workday across monitored Afghan markets?

## Data source

The raw data come from the World Food Programme food-price data for Afghanistan, distributed through the [Humanitarian Data Exchange](https://data.humdata.org/dataset/wfp-food-prices-for-afghanistan).

The analysis uses:

- `Wage (non-qualified labour, non-agricultural)` in AFN per day
- `Wheat flour (low quality)` in AFN per kilogram
- Retail, aggregate-flagged observations
- 34 market identifiers with paired wage and flour series across May 2020 to December 2025

## Method

For each market and month:

```text
Flour purchasing power = reported daily wage (AFN/day) / flour price (AFN/kg)
```

The result is kilograms of low-quality wheat flour purchasable with one reported paid workday. Monthly results use the median of available market-specific ratios. This is not the same as dividing the median wage by the median flour price.

## Key findings

| Benchmark month | Median purchasing power | Median wage | Median flour price | Markets |
|---|---:|---:|---:|---:|
| May 2020 | 8.81 kg/workday | AFN 300.00/day | AFN 34.25/kg | 34 |
| June 2022 | 5.78 kg/workday | AFN 300.00/day | AFN 51.28/kg | 34 |
| July 2024 | 12.57 kg/workday | AFN 300.00/day | AFN 26.25/kg | 34 |
| December 2025 | 10.04 kg/workday | AFN 300.00/day | AFN 29.00/kg | 34 |

- Purchasing power declined 34.41% from May 2020 to June 2022.
- It increased 117.47% from the June 2022 low to the July 2024 peak.
- It declined 20.08% from the July 2024 peak to December 2025.
- December 2025 purchasing power ranged from 6.94 kg/workday in Nuristan to 14.58 kg/workday in Nimroz among the highlighted markets.
- A fixed-coverage sensitivity analysis excluding Daykundi produced a maximum monthly median difference of 0.219 kg/workday.

## Data quality and validation

- Audited missing fields, dates, numeric values, nonpositive prices, duplicates, and market identifiers.
- Reviewed 46 large consecutive monthly changes against the raw CSV and documented each decision.
- Identified one missing Daykundi wage observation in February 2025.
- Reproduced the calculation in Python and passed 16 comparisons with displayed Power BI values.

## Tools

- Excel for inspection, review documentation, and analytical tables
- Power BI for data modeling, measures, dashboarding, and visual validation
- Python for reproducibility checks and outputs

## Project structure

```text
data/raw/                         Raw WFP price and market files
data/processed/                   Processed analysis output
dashboard/                        Power BI dashboard
outputs/tables/                   Audit, research, and validation tables
paper/                            Final research paper
presentation/                     Presentation and speaker script
src/                              Reproducible analysis and validation scripts
portfolio/                        CV wording and portfolio materials
```

## Reproduce the validation

Run the following script with a Python environment that includes the project dependencies:

```powershell
python src/04_reproduce_analysis.py
```

It recreates the market-month analysis, validates the key results, and writes outputs under `outputs/tables/python_validation/`.

## Important limitations

This indicator describes the flour value of one reported paid workday. It does not measure employment availability, total household income, food consumption, nutrition, or national welfare. The monitored markets are not demonstrated to be a probability sample of all Afghan households or all trading locations. The analysis is descriptive and does not attribute observed changes to particular events or policies.

## Portfolio deliverables

- [Final research paper](paper/Final_Paper.docx)
- [PowerPoint presentation](presentation/Afghanistan_Food_Purchasing_Power_Presentation.pptx)
- [Speaker script](presentation/Speaker_Script_Afghanistan_Food_Purchasing_Power.docx)
- [Python validation script](src/04_reproduce_analysis.py)
