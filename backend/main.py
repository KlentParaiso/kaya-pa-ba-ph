import os
import sqlite3
from datetime import date
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = os.getenv('DB_PATH', str(Path(__file__).parent/'cpi.sqlite3'))
app = FastAPI(title='Kaya Pa Ba PH API')
DEFAULT_ORIGINS = 'http://localhost:5173,http://127.0.0.1:5173'
allowed = [o.strip() for o in os.getenv('FRONTEND_ORIGINS', DEFAULT_ORIGINS).split(',') if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed, allow_methods=['GET','POST'],allow_headers=['Content-Type'])

def connect():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    return conn

def setup():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS cpi_observations (
           region TEXT NOT NULL, month TEXT NOT NULL, cpi REAL NOT NULL CHECK(cpi>0),
           base_year TEXT NOT NULL, source_url TEXT NOT NULL,
           publication_date TEXT NOT NULL, status TEXT NOT NULL,
           PRIMARY KEY(region,month,base_year))""")
setup()

class Budget(BaseModel):
    income: float=Field(ge=0,le=1e9)
    rent: float=Field(ge=0,le=1e9)
    food: float=Field(ge=0,le=1e9)
    transport: float=Field(ge=0,le=1e9)
    utilities: float=Field(ge=0,le=1e9)
    other: float=Field(ge=0,le=1e9)

@app.get('/health')
def health(): return {'status':'ok'}

@app.post('/budget')
def budget(b:Budget):
    total=sum([b.rent,b.food,b.transport,b.utilities,b.other])
    return {'total_expenses':round(total,2),'remaining':round(b.income-total,2),
            'expense_ratio':round(total/b.income,5) if b.income else None}

@app.get('/cpi/observations')
def observations(region:str='Philippines'):
    with connect() as db:
        rows=db.execute('SELECT * FROM cpi_observations WHERE region=? AND status="published" ORDER BY month', (region,)).fetchall()
    return {'observations':[dict(x) for x in rows]}

class Compare(BaseModel):
    amount:float=Field(ge=0,le=1e9)
    region:str='Philippines'
    earlier_month:str
    later_month:str

@app.post('/cpi/compare')
def compare(req:Compare):
    if req.earlier_month>=req.later_month:
        raise HTTPException(422,'Earlier month must precede later month')
    with connect() as db:
        records=db.execute('SELECT * FROM cpi_observations WHERE region=? AND month IN (?,?) AND status="published"',
            (req.region,req.earlier_month,req.later_month)).fetchall()
    bymonth={x['month']:dict(x) for x in records}
    if req.earlier_month not in bymonth or req.later_month not in bymonth:
        raise HTTPException(404,'Matching verified CPI observations not available')
    a,b=bymonth[req.earlier_month],bymonth[req.later_month]
    if a['base_year']!=b['base_year']:
        raise HTTPException(422,'CPI base years do not match')
    adjusted=round(req.amount*b['cpi']/a['cpi'],2)
    return {'adjusted_amount':adjusted,'difference':round(adjusted-req.amount,2),
            'earlier':a,'later':b,'method':'amount × later CPI ÷ earlier CPI'}

