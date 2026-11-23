"""Screen selected series; flags request review, never automatic deletion.
Run: python src/03_review_values.py (standard library only).
"""
from pathlib import Path
import csv, json, statistics
from collections import defaultdict, Counter
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/tables/audit'
OUT.mkdir(parents=True,exist_ok=True)
TARGETS={'Wage (non-qualified labour, non-agricultural)':'Day','Wheat flour (low quality)':'KG'}
with (ROOT/'data/raw/wfp_food_prices_afg.csv').open(encoding='utf-8-sig',newline='') as f:
    rows=[r for r in csv.DictReader(f) if '2020-05'<=r['date'][:7]<='2025-12' and r['commodity'] in TARGETS and r['unit']==TARGETS[r['commodity']] and r['currency']=='AFN' and r['pricetype']=='Retail']
def save(name, data, fields=None):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(data[0]));w.writeheader();w.writerows(data)
groups=defaultdict(list)
for r in rows: groups[r['commodity']].append(r)
summary=[]
for c,rs in groups.items():
    vals=[float(r['price']) for r in rs]
    summary.append(dict(commodity=c,unit=TARGETS[c],observations=len(rs),market_ids=len(set(r['market_id'] for r in rs)),minimum=min(vals),median=statistics.median(vals),maximum=max(vals),priceflag_counts=json.dumps(dict(Counter(r['priceflag'] for r in rs)))))
save('selected_value_summary.csv',summary)
series=defaultdict(list)
for r in rows:series[r['market_id'],r['commodity']].append(r)
checks=[]
for key,rs in series.items():
    rs.sort(key=lambda r:r['date'])
    for prev,cur in zip(rs,rs[1:]):
        py,pm=map(int,prev['date'][:7].split('-'));cy,cm=map(int,cur['date'][:7].split('-'))
        if (cy*12+cm)-(py*12+pm)!=1: continue
        old,new=float(prev['price']),float(cur['price'])
        if old<=0:continue
        change=(new/old-1)*100
        if abs(change)>=25:
            checks.append(dict(market_id=cur['market_id'],market=cur['market'],commodity=cur['commodity'],unit=cur['unit'],previous_month=prev['date'][:7],month=cur['date'][:7],previous_price=old,price=new,change_percent=round(change,4),priceflag=cur['priceflag'],review_status='Unreviewed',review_note=''))
checks.sort(key=lambda r:abs(r['change_percent']),reverse=True)
fields=['market_id','market','commodity','unit','previous_month','month','previous_price','price','change_percent','priceflag','review_status','review_note']
save('large_monthly_changes_review.csv',checks,fields)
extremes=[]
for c,rs in groups.items():
    ordered=sorted(rs,key=lambda r:float(r['price']))
    for label,rr in [('lowest',ordered[:5]),('highest',ordered[-5:])]:
        for r in rr:extremes.append(dict(extreme=label,market_id=r['market_id'],market=r['market'],month=r['date'][:7],commodity=c,unit=r['unit'],price=r['price'],priceflag=r['priceflag']))
save('selected_extreme_values.csv',extremes)
print(json.dumps({'summary':summary,'review_threshold_absolute_percent':25,'flagged_consecutive_month_changes':len(checks),'top_five':checks[:5]},indent=2))
