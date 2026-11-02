"""Import human-verified, normalized PSA observations (never raw arbitrary PSA exports)."""
import csv,sys
from datetime import datetime
from urllib.parse import urlparse
from main import connect,setup
COLUMNS={'region','month','cpi','base_year','source_url','publication_date','status'}
def valid_date(s): datetime.strptime(s,'%Y-%m-%d');return s
def main(path):
    with open(path,encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    if not rows: raise ValueError('CSV is empty')
    if set(rows[0])!=COLUMNS: raise ValueError(f'Expected columns: {sorted(COLUMNS)}')
    checked=[]
    for i,r in enumerate(rows,2):
        month=r['month']; valid_date(month+'-01')
        if len(month)!=7: raise ValueError(f'Row {i}: month must be YYYY-MM')
        value=float(r['cpi'])
        if value<=0: raise ValueError(f'Row {i}: CPI must be positive')
        if r['status']!='published': raise ValueError(f'Row {i}: only verified published rows accepted')
        if not r['region'].strip() or not r['base_year'].strip(): raise ValueError(f'Row {i}: missing region/base year')
        url=urlparse(r['source_url'])
        if url.scheme!='https' or url.hostname not in {'psa.gov.ph','openstat.psa.gov.ph'}:
            raise ValueError(f'Row {i}: supply exact official PSA source URL')
        valid_date(r['publication_date'])
        checked.append((r['region'],month,value,r['base_year'],r['source_url'],r['publication_date'],r['status']))
    with connect() as db:
        db.executemany("""INSERT INTO cpi_observations VALUES (?,?,?,?,?,?,?)
        ON CONFLICT(region,month,base_year) DO UPDATE SET cpi=excluded.cpi,
        source_url=excluded.source_url,publication_date=excluded.publication_date,status=excluded.status""",checked)
    print(f'Imported {len(checked)} verified observations')
if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: python import_cpi.py path/to/verified.csv')
    main(sys.argv[1])

