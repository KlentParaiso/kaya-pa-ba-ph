from fastapi.testclient import TestClient
from main import app
client=TestClient(app)
def test_health(): assert client.get('/health').json()=={'status':'ok'}
def test_budget():
    response=client.post('/budget',json={'income':25000,'rent':5000,'food':6000,'transport':2500,'utilities':2000,'other':1500})
    assert response.status_code==200
    assert response.json()['total_expenses']==17000
    assert response.json()['remaining']==8000
def test_reject_negative():
    response=client.post('/budget',json={'income':-1,'rent':0,'food':0,'transport':0,'utilities':0,'other':0})
    assert response.status_code==422
def test_missing_cpi():
    r=client.post('/cpi/compare',json={'amount':25000,'region':'UNKNOWN','earlier_month':'2025-01','later_month':'2026-01'})
    assert r.status_code==404

def test_cors_allows_local_dev_origins():
    for origin in ['http://localhost:5173','http://127.0.0.1:5173']:
        r=client.options('/budget',headers={'Origin':origin,'Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'})
        assert r.status_code==200
        assert r.headers['access-control-allow-origin']==origin
