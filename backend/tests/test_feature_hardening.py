from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app import api

client = TestClient(app)


def reset():
    api.REQUESTS.clear(); api.EVIDENCE.clear(); api.APPROVALS.clear(); api.EVENTS.clear()


def request_data(request_id="feature-req-1234"):
    return {"request_id": request_id, "agent_id": "invoice-agent-07", "credential_id": "cred-invoice-07", "tool": "invoice_db", "action": "invoice.read", "resource": "invoices", "requested_scope": 20, "context": {"external": True, "sensitive": True}}


def test_approval_expires_without_execution():
    reset()
    body = client.post('/api/v1/decisions', json=request_data()).json()
    approval_id = body['approval_id']
    item = api.APPROVALS[approval_id]
    item['expires_at'] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    response = client.post(f'/api/v1/approvals/{approval_id}', json={"approved": True, "approver": "reviewer", "reason": "late"})
    assert response.status_code == 200
    assert response.json()['decision'] == 'DENY'
    assert response.json()['lifecycle'] == 'DENIED'
    assert item['status'] == 'EXPIRED'
    assert not any(e['event'] == 'EXECUTION_COMPLETED' for e in api.EVENTS)


def test_audit_integrity_chain_verifies():
    reset()
    client.post('/api/v1/decisions', json=request_data('integrity-1234'))
    result = client.get('/api/v1/audit/integrity').json()
    assert result['valid'] is True
    assert result['events'] > 0


def test_audit_integrity_detects_tampering():
    reset()
    client.post('/api/v1/decisions', json=request_data('tamper-audit-1'))
    api.EVENTS[0]['event'] = 'TAMPERED'
    result = client.get('/api/v1/audit/integrity').json()
    assert result['valid'] is False
