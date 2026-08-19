from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def payload(**changes):
    p={'request_id':'req-api-123456','agent_id':'invoice-agent-07','credential_id':'cred-invoice-07','tool':'invoice_db','action':'invoice.read','resource':'invoices','requested_scope':20}
    p.update(changes); return p

def test_health():
    assert client.get('/healthz').json()=={'status':'ok'}

def test_ready():
    assert client.get('/readyz').status_code==200

def test_index():
    r=client.get('/'); assert r.status_code==200; assert 'ActionPermit' in r.text

def test_decision_and_idempotency():
    p=payload(); r=client.post('/api/v1/decisions',json=p,headers={'X-Request-ID':p['request_id']}); assert r.status_code==200
    first=r.json(); second=client.post('/api/v1/decisions',json=p).json(); assert second==first

def test_header_mismatch():
    assert client.post('/api/v1/decisions',json=payload(),headers={'X-Request-ID':'wrong-id'}).status_code==400

def test_audit_missing():
    assert client.get('/api/v1/audit/not-found').status_code==404
