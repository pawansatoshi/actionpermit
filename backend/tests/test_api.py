from fastapi.testclient import TestClient
from app.main import app
from app.api import REQUESTS, EVIDENCE, APPROVALS, EVENTS

client = TestClient(app)


def reset_state():
    REQUESTS.clear(); EVIDENCE.clear(); APPROVALS.clear(); EVENTS.clear()


def base_request(**changes):
    data = {'request_id':'req-api-12345678','agent_id':'invoice-agent-07','credential_id':'cred-invoice-07','tool':'invoice_db','action':'invoice.read','resource':'invoices','requested_scope':20}
    data.update(changes)
    return data


def test_allow_executes_and_audits():
    reset_state()
    body = client.post('/api/v1/decisions', json=base_request()).json()
    assert body['decision'] == 'ALLOW'
    assert body['lifecycle'] == 'COMPLETED'
    audit = client.get(f"/api/v1/audit/{body['evidence_id']}").json()
    assert audit['verified'] is True
    assert any(e['event'] == 'EXECUTION_COMPLETED' for e in audit['events'])


def test_external_sensitive_request_requires_and_accepts_approval():
    reset_state()
    body = client.post('/api/v1/decisions', json=base_request(request_id='req-api-approval1', context={'external':True,'sensitive':True})).json()
    assert body['decision'] == 'REQUIRE_APPROVAL'
    r = client.post(f"/api/v1/approvals/{body['approval_id']}", json={'approved':True,'approver':'security-reviewer','reason':'Verified demo action'})
    body2 = r.json()
    assert body2['decision'] == 'ALLOW'
    assert body2['lifecycle'] == 'COMPLETED'


def test_approval_rejection_never_executes():
    reset_state()
    body = client.post('/api/v1/decisions', json=base_request(request_id='req-api-reject1', context={'external':True,'sensitive':True})).json()
    body = client.post(f"/api/v1/approvals/{body['approval_id']}", json={'approved':False,'approver':'security-reviewer','reason':'Not authorized'}).json()
    assert body['decision'] == 'DENY'
    assert body['execution_id'] is None


def test_idempotency_returns_same_decision():
    reset_state()
    payload = base_request(request_id='req-api-idempotent')
    first = client.post('/api/v1/decisions', json=payload).json()
    second = client.post('/api/v1/decisions', json=payload).json()
    assert second == first
