"""Read-only audit of WFP source data. Run with Python and pandas installed.

From the project directory: python src/01_audit_data.py
Outputs are descriptive audit tables, not a cleaned research dataset.
"""
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'tables' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
price_path = ROOT / 'data/raw/wfp_food_prices_afg.csv'
market_path = ROOT / 'data/raw/wfp_markets_afg.csv'
p = pd.read_csv(price_path, dtype={'market_id': str, 'commodity_id': str})
m = pd.read_csv(market_path, dtype={'market_id': str})
original_columns = list(p.columns)
p['parsed_date'] = pd.to_datetime(p['date'], errors='coerce')
p['month'] = p['parsed_date'].dt.to_period('M').astype(str)
p['numeric_price'] = pd.to_numeric(p['price'], errors='coerce')
key = ['date', 'market_id', 'commodity_id', 'unit', 'pricetype', 'currency']
summary = {
    'price_rows': len(p), 'market_lookup_rows': len(m),
    'price_market_ids': int(p.market_id.nunique()),
    'lookup_unique_market_ids': int(m.market_id.nunique()),
    'lookup_duplicate_id_rows': int(m.market_id.duplicated(keep=False).sum()),
    'unmatched_price_market_ids': sorted(set(p.market_id) - set(m.market_id)),
    'invalid_dates': int(p.parsed_date.isna().sum()),
    'missing_or_nonnumeric_prices': int(p.numeric_price.isna().sum()),
    'nonpositive_prices': int(p.numeric_price.le(0).sum()),
    'exact_duplicate_rows_beyond_first': int(p[original_columns].duplicated().sum()),
    'duplicate_key_rows': int(p.duplicated(key, keep=False).sum()),
    'duplicate_key_definition': key,
    'priceflag_counts': p.priceflag.value_counts(dropna=False).to_dict(),
    'pricetype_counts': p.pricetype.value_counts(dropna=False).to_dict(),
    'source_sha256': {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in [price_path, market_path]},
}
p[original_columns].isna().sum().rename('missing_rows').to_csv(OUT/'missing_values.csv')
p.groupby(['commodity','unit'], dropna=False).size().rename('rows').to_csv(OUT/'commodity_units.csv')
p.groupby(['commodity','priceflag'], dropna=False).size().rename('rows').to_csv(OUT/'commodity_flags.csv')
p[p.duplicated(key, keep=False)][original_columns].to_csv(OUT/'duplicate_keys.csv', index=False)
coverage = p.groupby(['market_id','market','commodity','unit','pricetype','currency'], dropna=False).agg(
    rows=('date','size'), first_date=('parsed_date','min'), last_date=('parsed_date','max'), observed_months=('month','nunique')).reset_index()
coverage.to_csv(OUT/'series_coverage.csv', index=False)

# Evaluate the proposed complete-year window, without assuming all flags are equivalent.
q = p[p.parsed_date.between('2019-01-01','2025-12-31') & p.currency.eq('AFN') & p.pricetype.eq('Retail') & p.numeric_price.gt(0)].copy()
wage = 'Wage (non-qualified labour, non-agricultural)'
flours = ['Wheat flour','Wheat flour (high quality)','Wheat flour (low quality)']
rows = []
for label, subset in [('all_flags', q), ('actual_only', q[q.priceflag.eq('actual')])]:
    w = subset[subset.commodity.eq(wage) & subset.unit.eq('Day')]
    # Multiple rows within a market/month are explicitly excluded, never silently averaged.
    wcount = w.groupby(['market_id','month']).size()
    wkeys = set(wcount[wcount.eq(1)].index)
    for flour in flours:
        f = subset[subset.commodity.eq(flour) & subset.unit.eq('KG')]
        fcount = f.groupby(['market_id','month']).size()
        fkeys = set(fcount[fcount.eq(1)].index)
        matched = wkeys & fkeys
        for mid in sorted(set(q.market_id)):
            count = sum(k[0] == mid for k in matched)
            rows.append({'flag_policy':label,'market_id':mid,'market':q.loc[q.market_id.eq(mid),'market'].iloc[0],
                         'flour':flour,'matched_months':count,'expected_months':84,
                         'coverage_percent':round(100*count/84,2),
                         'ambiguous_wage_months':int(sum(k[0]==mid for k in wcount[wcount.gt(1)].index)),
                         'ambiguous_flour_months':int(sum(k[0]==mid for k in fcount[fcount.gt(1)].index))})
matches = pd.DataFrame(rows)
matches.to_csv(OUT/'wage_flour_coverage_2019_2025.csv', index=False)
compact = matches.groupby(['flag_policy','flour']).agg(matched_market_months=('matched_months','sum'), markets_with_matches=('matched_months',lambda s:int(s.gt(0).sum())), markets_with_84_months=('matched_months',lambda s:int(s.eq(84).sum()))).reset_index()
compact.to_csv(OUT/'matching_summary.csv', index=False)

# Independently verify the saved Excel pivot counts against the raw CSV.
import openpyxl
wb = openpyxl.load_workbook(ROOT/'outputs/tables/initial_inspection.xlsx', read_only=True, data_only=True)
unit_counts = p.groupby(['commodity','unit']).size()
unit_checks = []
sheet = wb['Sheet3']
for r in range(5,21):
    commodity = sheet.cell(r,1).value
    for col, unit in [(2,'Day'),(3,'KG'),(4,'L'),(5,'Unit'),(6,'USD/LCU')]:
        unit_checks.append((sheet.cell(r,col).value or 0) == int(unit_counts.get((commodity,unit),0)))
flag_checks = [int(p.priceflag.eq(wb['Sheet4'].cell(r,1).value).sum()) == wb['Sheet4'].cell(r,2).value for r in range(4,7)]
summary['saved_pivot_unit_cells_match_csv'] = all(unit_checks)
summary['saved_pivot_flag_cells_match_csv'] = all(flag_checks)
summary['saved_pivot_grand_totals_match_csv'] = wb['Sheet3']['G21'].value == wb['Sheet4']['B7'].value == len(p)
wb.close()
(OUT/'audit_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2))
print(compact.to_string(index=False))
