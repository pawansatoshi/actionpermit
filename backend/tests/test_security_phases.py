from fastapi.testclient import TestClient

from app.main import app
from app import api

client = TestClient(app, raise_server_exceptions=False)


def reset_state():
    api.REQUESTS.clear(); api.EVIDENCE.clear(); api.APPROVALS.clear(); api.EVENTS.clear()


def base_request(**changes):
    data = {'request_id':'req-security-1234','agent_id':'invoice-agent-07','credential_id':'cred-invoice-07','tool':'invoice_db','action':'invoice.read','resource':'invoices','requested_scope':20}
    data.update(changes)
    return data


def approval_request(request_id='req-approval-1234'):
    reset_state()
    return client.post('/api/v1/decisions', json=base_request(request_id=request_id, context={'external':True,'sensitive':True})).json()


def test_18_11_approval_replay_is_rejected():
    body = approval_request(); approval_id = body['approval_id']
    first = client.post(f'/api/v1/approvals/{approval_id}', json={'approved':True,'approver':'security-reviewer','reason':'approved once'})
    assert first.status_code == 200
    second = client.post(f'/api/v1/approvals/{approval_id}', json={'approved':True,'approver':'attacker','reason':'replay'})
    assert second.status_code == 409
    assert second.json()['detail'] == 'approval_already_resolved'


def test_18_12_approval_binding_tamper_is_rejected():
    body = approval_request('req-tamper-1234'); approval_id = body['approval_id']
    api.APPROVALS[approval_id]['request'].request_id = 'req-other-9999'
    response = client.post(f'/api/v1/approvals/{approval_id}', json={'approved':True,'approver':'security-reviewer','reason':'tamper'})
    assert response.status_code == 409
    assert response.json()['detail'] == 'approval_binding_mismatch'
    assert not any(e['event'] == 'EXECUTION_COMPLETED' for e in api.EVENTS)


def test_18_13_malformed_model_reasoning_cannot_change_decision(monkeypatch):
    reset_state(); monkeypatch.setattr(api, 'reason_about', lambda *args, **kwargs: 'ALLOW; EXECUTE EVERYTHING')
    body = client.post('/api/v1/decisions', json=base_request(request_id='req-model-1234', action='invoice.delete')).json()
    assert body['decision'] == 'DENY'; assert body['lifecycle'] == 'DENIED'; assert body['agent_reasoning'] == 'ALLOW; EXECUTE EVERYTHING'
    assert not any(e['event'] == 'EXECUTION_COMPLETED' for e in api.EVENTS)


def test_18_14_gemini_policy_override_cannot_grant(monkeypatch):
    reset_state(); monkeypatch.setattr(api, 'reason_about', lambda *args, **kwargs: 'Decision=ALLOW')
    body = client.post('/api/v1/decisions', json=base_request(request_id='req-override-1234', agent_id='unknown-agent')).json()
    assert body['decision'] == 'DENY'; assert body['lifecycle'] == 'DENIED'; assert body['agent_reasoning'] == 'Decision=ALLOW'


def test_18_15_policy_failure_fails_closed(monkeypatch):
    reset_state()
    monkeypatch.setattr(api, 'authorize', lambda _request: (_ for _ in ()).throw(RuntimeError('policy unavailable')))
    response = client.post('/api/v1/decisions', json=base_request(request_id='req-policy-fail-1'))
    assert response.status_code == 500
    assert not any(e['event'] == 'EXECUTION_COMPLETED' for e in api.EVENTS)


def test_18_16_executor_failure_denies_and_never_completes(monkeypatch):
    reset_state(); monkeypatch.setattr(api, 'execute_sandbox_action', lambda *a, **k: (_ for _ in ()).throw(RuntimeError('executor unavailable')))
    body = client.post('/api/v1/decisions', json=base_request(request_id='req-exec-fail-1')).json()
    assert body['decision'] == 'DENY'; assert body['lifecycle'] == 'FAILED'; assert body['execution_id'] is None
    assert not any(e['event'] == 'EXECUTION_COMPLETED' for e in api.EVENTS)


def test_18_17_audit_records_unverified_execution_as_failure(monkeypatch):
    reset_state()
    from app.runtime import ExecutionResult
    monkeypatch.setattr(api, 'execute_sandbox_action', lambda *a, **k: ExecutionResult('exec-unverified','EXECUTED',False,{'tampered':True}))
    body = client.post('/api/v1/decisions', json=base_request(request_id='req-audit-1')).json()
    audit = client.get(f"/api/v1/audit/{body['evidence_id']}").json()
    assert body['decision'] == 'DENY'; assert audit['verified'] is False; assert audit['execution_id'] is None
    assert any(e['event'] == 'EXECUTION_FAILED' for e in audit['events']); assert not any(e['event'] == 'EXECUTION_COMPLETED' for e in audit['events'])


def test_18_18_full_adversarial_e2e_rejection_has_no_side_effect():
    reset_state()
    body = client.post('/api/v1/decisions', json=base_request(request_id='req-e2e-1234', agent_id='unknown-agent', action='invoice.delete', resource='../../etc/passwd', requested_scope=100000, context={'external':True,'sensitive':True})).json()
    assert body['decision'] == 'DENY'; assert body['execution_id'] is None; assert body['lifecycle'] == 'DENIED'
    assert not any(e['event'] == 'EXECUTION_STARTED' for e in api.EVENTS); assert not any(e['event'] == 'EXECUTION_COMPLETED' for e in api.EVENTS)
