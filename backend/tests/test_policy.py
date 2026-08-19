from app.models import ActionRequest, Decision
from app.policy import authorize

def req(**changes):
    data={'request_id':'req-12345678','agent_id':'invoice-agent-07','credential_id':'cred-invoice-07','tool':'invoice_db','action':'invoice.read','resource':'invoices','requested_scope':20}
    data.update(changes)
    return ActionRequest(**data)

def test_valid_request_allows():
    assert authorize(req())[0] is Decision.ALLOW

def test_unknown_agent_denies():
    assert authorize(req(agent_id='unknown'))[0] is Decision.DENY

def test_credential_mismatch_denies():
    assert authorize(req(credential_id='wrong'))[0] is Decision.DENY

def test_capability_escalation_denies():
    assert authorize(req(action='invoice.delete'))[0] is Decision.DENY

def test_scope_escalation_denies():
    assert authorize(req(requested_scope=101))[0] is Decision.DENY

def test_zero_scope_denies():
    assert authorize(req(requested_scope=0))[0] is Decision.DENY
