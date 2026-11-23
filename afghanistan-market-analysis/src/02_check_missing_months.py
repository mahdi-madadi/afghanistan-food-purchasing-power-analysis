"""Identify calendar gaps without changing raw data or the Excel workbook.
Run from project root: python src/02_check_missing_months.py
Only the optional workbook inspection requires openpyxl.
"""
from pathlib import Path
import csv
import json
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/tables/audit'
OUT.mkdir(parents=True, exist_ok=True)
with (ROOT/'data/raw/wfp_food_prices_afg.csv').open(encoding='utf-8-sig', newline='') as f:
    raw = list(csv.DictReader(f))
wage = 'Wage (non-qualified labour, non-agricultural)'
flour = 'Wheat flour (low quality)'
months = [f'{y}-{m:02d}' for y in range(2019,2026) for m in range(1,13)]
observations = defaultdict(list)
names = {}
full_dates = defaultdict(list)
for r in raw:
    if r['commodity'] not in [wage, flour]:
        continue
    kind = 'wage' if r['commodity'] == wage else 'flour'
    expected_unit = 'Day' if kind == 'wage' else 'KG'
    if r['currency'] != 'AFN' or r['pricetype'] != 'Retail' or r['unit'] != expected_unit or float(r['price']) <= 0:
        continue
    mid, month = r['market_id'], r['date'][:7]
    names[mid] = r['market']
    full_dates[mid,kind].append(month)
    if month in months:
        observations[mid,month,kind].append(r)

# Retain the same 34-market cohort with at least one unambiguous match.
markets = sorted(mid for mid in names if any(len(observations[mid,t,'wage']) == len(observations[mid,t,'flour']) == 1 for t in months))
rows = []
for mid in markets:
    for month in months:
        w, f = observations[mid,month,'wage'], observations[mid,month,'flour']
        if len(w)>1 or len(f)>1:
            status = 'ambiguous_multiple_records'
        elif w and f:
            status = 'matched'
        elif w:
            status = 'flour_missing'
        elif f:
            status = 'wage_missing'
        else:
            status = 'both_missing'
        rows.append(dict(market_id=mid,market=names[mid],month=month,status=status,wage_rows=len(w),flour_rows=len(f),
                         wage_flags=';'.join(sorted(set(r['priceflag'] for r in w))),
                         flour_flags=';'.join(sorted(set(r['priceflag'] for r in f)))))
def save(name, records):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
save('monthly_matching_status_2019_2025.csv',rows)
gaps=[r for r in rows if r['status']!='matched']
save('missing_months_2019_2025.csv',gaps)
monthly=[]
for month in months:
    counts=Counter(r['status'] for r in rows if r['month']==month)
    monthly.append(dict(month=month,markets_in_cohort=len(markets),matched=counts['matched'],
                        wage_missing=counts['wage_missing'],flour_missing=counts['flour_missing'],
                        both_missing=counts['both_missing'],ambiguous=counts['ambiguous_multiple_records']))
save('monthly_coverage_summary.csv',monthly)
series=[]
for mid in markets:
    series.append(dict(market_id=mid,market=names[mid],first_wage_month=min(full_dates[mid,'wage']),
                       first_flour_month=min(full_dates[mid,'flour']),last_wage_month=max(full_dates[mid,'wage']),last_flour_month=max(full_dates[mid,'flour'])))
save('target_series_dates.csv',series)
summary={'cohort_markets':len(markets),'calendar_months':len(months),'status_counts':dict(Counter(r['status'] for r in rows)),
         'months_without_any_matches':[r for r in monthly if r['matched']==0],
         'partially_matched_months':[r for r in monthly if 0<r['matched']<len(markets)],
         'fully_matched_months':[r['month'] for r in monthly if r['matched']==len(markets)],
         'gaps_in_months_with_some_matches':[r for r in gaps if any(x['month']==r['month'] and x['matched']>0 for x in monthly)]}
(OUT/'missing_months_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))

# Inspect saved workbook only; never save or modify it.
try:
    import openpyxl
    wb=openpyxl.load_workbook(ROOT/'outputs/tables/initial_inspection.xlsx',read_only=False,data_only=True)
    inventory=[]
    for s in wb:
        item={'sheet':s.title,'rows':s.max_row,'columns':s.max_column,'autofilter_range':s.auto_filter.ref,
              'filter_columns':[str(c) for c in s.auto_filter.filterColumn],
              'tables':list(s.tables)}
        if s.max_row<1000:
            item['first_rows']=list(s.iter_rows(min_row=1,max_row=min(5,s.max_row),max_col=min(9,s.max_column),values_only=True))
        inventory.append(item)
    wb.close()
    (OUT/'saved_workbook_inspection.json').write_text(json.dumps(inventory,indent=2,default=str),encoding='utf-8')
    print('WORKBOOK',json.dumps(inventory,default=str))
except ImportError:
    print('Workbook inspection skipped: install openpyxl to inspect workbook.')
