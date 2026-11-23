"""Reproduce the Power BI analysis from the original WFP CSV.

Run: python src/04_reproduce_analysis.py
Uses only Python's standard library. Never edits the source CSV, Excel or PBIX.
"""
from pathlib import Path
from collections import defaultdict
from statistics import median, quantiles
from datetime import datetime, timezone
import csv
import hashlib
import json
import platform

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/raw/wfp_food_prices_afg.csv'
TABLES = ROOT / 'outputs/tables/python_validation'
PROCESSED = ROOT / 'data/processed'
for directory in (TABLES, PROCESSED):
    directory.mkdir(parents=True, exist_ok=True)

def require(condition, message):
    if not condition:
        raise ValueError(message)

def write_csv(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

# 1. Select the same commodities, units, price flags and dates as Power BI.
definitions = {
    'Wage (non-qualified labour, non-agricultural)': ('wage', '465', 'Day'),
    'Wheat flour (low quality)': ('flour', '800', 'KG'),
}
series = {'wage': {}, 'flour': {}}
with SOURCE.open(encoding='utf-8-sig', newline='') as stream:
    for row in csv.DictReader(stream):
        month = row['date'][:7]
        if not ('2020-05' <= month <= '2025-12') or row['commodity'] not in definitions:
            continue
        kind, commodity_id, unit = definitions[row['commodity']]
        if (row['unit'], row['currency'], row['pricetype'], row['priceflag']) != (unit, 'AFN', 'Retail', 'aggregate'):
            continue
        require(row['commodity_id'] == commodity_id, 'Commodity ID changed: inspect source.')
        value = float(row['price'])
        require(value > 0, 'Nonpositive value: inspect source.')
        key = (int(row['market_id']), month)
        require(key not in series[kind], f'Duplicate market/month in {kind}: {key}')
        series[kind][key] = row

require(len(series['wage']) == 2311, 'Expected 2,311 wage rows for this source snapshot.')
require(len(series['flour']) == 2312, 'Expected 2,312 flour rows for this source snapshot.')
require(set(series['wage']).issubset(series['flour']), 'Wage keys absent from flour table.')
require(set(series['flour']) - set(series['wage']) == {(3692, '2025-02')}, 'Unexpected missing wage keys.')

# 2. Left join wages onto flour using market_id AND month; retain the missing wage.
panel = []
for (market_id, month), flour in sorted(series['flour'].items()):
    wage = series['wage'].get((market_id, month))
    flour_price = float(flour['price'])
    daily_wage = float(wage['price']) if wage else None
    if wage:
        require(wage['market'] == flour['market'], f'Market label mismatch: {market_id}')
    panel.append({
        'month': month + '-01', 'market_id': market_id, 'market': flour['market'],
        'flour_afn_per_kg': flour_price, 'flour_priceflag': flour['priceflag'],
        'wage_afn_per_day': daily_wage, 'wage_priceflag': wage['priceflag'] if wage else None,
        'flour_kg_per_workday': daily_wage / flour_price if wage else None,
    })
require(len({r['market_id'] for r in panel}) == 34, 'Expected 34 market IDs.')
write_csv(PROCESSED / 'market_monthly_python.csv', panel)

# 3. Compute monthly medians, inclusive percentiles and fixed-33 sensitivity.
by_month = defaultdict(list)
for row in panel:
    by_month[row['month']].append(row)
require(len(by_month) == 68, 'Expected 68 calendar months.')
monthly = []
for month, rows in sorted(by_month.items()):
    require(len(rows) == 34, f'Incomplete flour coverage: {month}')
    valid = [r for r in rows if r['flour_kg_per_workday'] is not None]
    fixed = [r for r in valid if r['market_id'] != 3692]
    require(len(fixed) == 33, f'Fixed panel is not complete: {month}')
    values = [r['flour_kg_per_workday'] for r in valid]
    q25, _, q75 = quantiles(values, n=4, method='inclusive')
    original_median = median(values)
    fixed_median = median(r['flour_kg_per_workday'] for r in fixed)
    monthly.append({
        'month': month, 'median_daily_wage': median(r['wage_afn_per_day'] for r in valid),
        'median_flour_price': median(r['flour_afn_per_kg'] for r in rows),
        'median_purchasing_power': original_median, 'markets_with_purchasing_power': len(valid),
        'p25': q25, 'p75': q75, 'iqr': q75-q25,
        'median_fixed_33': fixed_median, 'fixed_market_count': len(fixed),
        'fixed_minus_original': fixed_median-original_median,
        'absolute_difference': abs(fixed_median-original_median),
    })
write_csv(TABLES / 'monthly_statistics.csv', monthly)
december = sorted(by_month['2025-12-01'], key=lambda r: (-r['flour_kg_per_workday'], r['market']))
write_csv(TABLES / 'december_2025_markets.csv', december)

# 4. Independently compare calculations with values recorded from Power BI.
expected = {
    '2020-05-01': (300.00, 34.25, 8.81),
    '2022-06-01': (300.00, 51.28, 5.78),
    '2024-07-01': (300.00, 26.25, 12.57),
    '2025-12-01': (300.00, 29.00, 10.04),
}
lookup = {r['month']: r for r in monthly}
checks = []
for month, targets in expected.items():
    for field, target in zip(['median_daily_wage','median_flour_price','median_purchasing_power'], targets):
        actual = lookup[month][field]
        checks.append(dict(month=month,metric=field,power_bi_displayed=target,python_value=actual,
                           tolerance=0.005,passed=abs(actual-target) <= 0.005+1e-12))
for field, target in [('p25',9.40),('p75',10.71),('iqr',1.31)]:
    actual=lookup['2025-12-01'][field]
    checks.append(dict(month='2025-12-01',metric=field,power_bi_displayed=target,python_value=actual,
                       tolerance=0.005,passed=abs(actual-target) <= 0.005+1e-12))
largest = max(monthly, key=lambda r:r['absolute_difference'])
checks.append(dict(month=largest['month'],metric='maximum_absolute_difference',power_bi_displayed=0.219,
                   python_value=largest['absolute_difference'],tolerance=0.0005,
                   passed=largest['month']=='2024-10-01' and abs(largest['absolute_difference']-0.219)<=0.0005))
require(lookup['2025-02-01']['markets_with_purchasing_power']==33, 'February market count differs.')
require(abs(lookup['2025-02-01']['fixed_minus_original'])<1e-12, 'February sensitivity differs.')
write_csv(TABLES/'power_bi_reconciliation.csv',checks)

# 5. Use full precision, not the rounded display values, for research comparisons.
low = min(monthly,key=lambda r:r['median_purchasing_power'])
high = max(monthly,key=lambda r:r['median_purchasing_power'])
require(low['month']=='2022-06-01' and high['month']=='2024-07-01', 'Extremum month differs.')
comparisons=[]
for label,start,end in [('First to lowest',monthly[0],low),('Lowest to highest',low,high),
                       ('Highest to final',high,monthly[-1]),('First to final',monthly[0],monthly[-1])]:
    comparisons.append(dict(comparison=label,start_month=start['month'],end_month=end['month'],
        start_value=start['median_purchasing_power'],end_value=end['median_purchasing_power'],
        percentage_change=100*(end['median_purchasing_power']/start['median_purchasing_power']-1)))
write_csv(TABLES/'full_precision_changes.csv',comparisons)
manifest={
    'source':str(SOURCE), 'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'run_at_utc':datetime.now(timezone.utc).isoformat(), 'python_version':platform.python_version(),
    'period':'2020-05 through 2025-12', 'panel_rows':len(panel), 'valid_ratios':sum(r['flour_kg_per_workday'] is not None for r in panel),
    'quantiles':'Inclusive linear interpolation, same convention as PERCENTILEX.INC.',
    'comparison_basis':'User-supplied Power BI displayed results; no PBIX internals inspected.',
    'minimum_months':[r['month'] for r in monthly if r['median_purchasing_power']==low['median_purchasing_power']],
    'maximum_months':[r['month'] for r in monthly if r['median_purchasing_power']==high['median_purchasing_power']],
    'all_display_checks_passed':all(r['passed'] for r in checks),
}
(TABLES/'run_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
require(manifest['all_display_checks_passed'], 'Reconciliation failed: inspect power_bi_reconciliation.csv.')
print('PASS: 2,312 rows; 2,311 valid ratios; 34 markets; 68 months; one missing Daykundi wage.')
print(f'PASS: all {len(checks)} comparisons with displayed Power BI results.')
for r in comparisons:print(f"{r['comparison']}: {r['percentage_change']:.6f}%")
print('Maximum sensitivity difference:', largest['month'], largest['absolute_difference'])
print('Tables saved to:',TABLES)
