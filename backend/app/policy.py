from dataclasses import dataclass
from .models import ActionRequest, Decision

@dataclass(frozen=True)
class AgentRecord:
    agent_id: str
    credential_id: str
    capabilities: frozenset[str]
    max_scope: int
    active: bool = True

AGENTS = {
    "invoice-agent-07": AgentRecord("invoice-agent-07", "cred-invoice-07", frozenset({"invoice.read"}), 100),
    "recon-agent-02": AgentRecord("recon-agent-02", "cred-recon-02", frozenset({"payment.read", "payment.reconcile"}), 50),
}

def authorize(request: ActionRequest) -> tuple[Decision, list[str]]:
    agent = AGENTS.get(request.agent_id)
    if agent is None:
        return Decision.DENY, ["unknown_agent"]
    if not agent.active:
        return Decision.DENY, ["agent_inactive"]
    if request.credential_id != agent.credential_id:
        return Decision.DENY, ["credential_mismatch"]
    if request.action not in agent.capabilities:
        return Decision.DENY, ["capability_not_granted"]
    if request.requested_scope > agent.max_scope:
        return Decision.DENY, ["scope_exceeded"]
    if request.requested_scope <= 0:
        return Decision.DENY, ["empty_scope"]
    return Decision.ALLOW, ["policy_satisfied"]
