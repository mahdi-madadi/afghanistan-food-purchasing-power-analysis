# Afghanistan WFP data — metadata and initial file inventory

Prepared: 15 November 2026. This document transcribes the supplied HDX metadata screenshot and separately records basic checks of the supplied CSV files. It is not a complete data-quality audit. Original files were not modified.

## 1. Source metadata transcribed from the screenshot

| Field | Value shown |
|---|---|
| Time period | 15 January 2000–15 November 2026 |
| Expected update frequency | Every month |
| Modified | 04 November 2026 |
| Contributor | WFP - World Food Programme |
| Source | FPMA, RRD, Vulnerability Analysis and Mapping (VAM) - WFP via FAO; GIEWS, WFP |
| Dataset added on HDX | 26 September 2018 |
| Location | Afghanistan |
| Methodology | Registry |
| Caveats / Comments | Although the frequency of updates is set to every month, updates may occur more or less frequently |
| License | Creative Commons Attribution for Intergovernmental Organisations (CC BY-IGO) |
| Tags | economics; food security; indicators; markets |
| Visibility | Public |

Transcription limitations:

- Dataset ID: not transcribed because the small text cannot be verified confidently from this screenshot. Copy the ID from the dataset page for the final research record.
- The screenshot does not expose hyperlink destinations or a license version; neither is inferred here.
- The downloads chart is a changing usage statistic, not research metadata, and is not transcribed.
- The source line preserves the visible acronyms without guessing their expansions.
- The modified date precedes the stated end of coverage. Both are preserved as displayed; they are not assumed to describe the same event.
- Download date and exact resource URLs were not supplied. The preparation date above is not a download date.
- This screenshot is dataset-level metadata; separate methodology for the market lookup has not been established.

## 2. Checks performed directly on the CSV files

| Item | Observed value |
|---|---|
| Price file | wfp_food_prices_afg.csv |
| Price records, excluding header | 45,737 |
| Price columns | 16 |
| Earliest date value | 2000-01-15 |
| Latest date value | 2026-11-15 |
| Distinct market IDs in price file | 40 |
| Distinct commodity labels | 16 |
| Currency labels | AFN |
| Price flags | actual; actual,aggregate; aggregate |
| Units | Day; KG; L; Unit; USD/LCU |
| Market lookup file | wfp_markets_afg.csv |
| Market lookup records, excluding header | 140 |
| Market lookup columns | 7 |

Price-file columns:

`date, admin1, admin2, market, market_id, latitude, longitude, category, commodity, commodity_id, unit, priceflag, pricetype, currency, price, usdprice`

Market-file columns:

`market_id, market, countryiso3, admin1, admin2, latitude, longitude`

Observed commodity labels:

- Bread
- Exchange rate
- Fuel (diesel)
- Livestock (sheep, one-year-old alive female)
- Oil (cooking)
- Pulses
- Rice (high quality)
- Rice (low quality)
- Salt
- Sugar
- Wage (non-qualified labour, non-agricultural)
- Wage (qualified labour)
- Wheat
- Wheat flour
- Wheat flour (high quality)
- Wheat flour (low quality)

## 3. Implications for our project

Both the unskilled wage series and flour-price series exist. This supports proceeding to a feasibility audit, but does not yet demonstrate sufficient same-market, same-month overlap.

1. Verify market-ID uniqueness and join coverage before merging the lookup. Its 140 rows must not be described as 140 markets with price observations.
2. Investigate actual and aggregate flags before calculating summaries, to avoid mixing or double-counting observations.
3. Keep plain, high-quality, and low-quality wheat flour separate until their definitions are checked.
4. Audit market-by-month coverage before selecting the study window. The overall date range does not imply complete observations for every series.
5. Investigate unusually large early wage values and historical currency/unit consistency before comparing the full time span. The first two wage records are 150000 and 100000 under an AFN label; no correction has been applied and no explanation has yet been established.
6. Match daily wages to flour priced per kilogram within the same market and period. The resulting ratio measures kilograms per paid workday, not actual monthly income or household food consumption.
7. Verify price and USD-price definitions against source documentation before using currency conversions.

## 4. Provenance and remaining work

Supplied source directory: `C:/Users/mahdi.madadi/Documents/Codex/afghanistan-market-analysis/`

- `data/raw/wfp_food_prices_afg.csv`
- `data/raw/wfp_markets_afg.csv`
- `data/metadata/metadata.png`

Suggested dataset landing page from the project research: https://data.humdata.org/dataset/wfp-food-prices-for-afghanistan . This URL was not extracted from the screenshot, and the live page was not reverified during this conversion.

Before final publication, add the exact download date, resource URLs, verified dataset ID, license link/version, source methodology, and file checksums. The next stage is a full audit of missing values, duplicate keys, market coverage, unit consistency, and wage–flour overlap.
