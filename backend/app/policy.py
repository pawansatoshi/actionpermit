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


@dataclass(frozen=True)
class PolicyResult:
    decision: Decision
    reasons: list[str]
    risk_score: int
    risk_level: str


def risk_for(request: ActionRequest) -> tuple[int, str, list[str]]:
    score = 0
    factors: list[str] = []
    if request.action.endswith(".delete"):
        score += 55
        factors.append("irreversible_action")
    if request.requested_scope > 50:
        score += 20
        factors.append("elevated_scope")
    if request.context.get("external"):
        score += 25
        factors.append("external_destination")
    if request.context.get("sensitive"):
        score += 20
        factors.append("sensitive_resource")
    score = min(score, 100)
    level = "LOW" if score <= 30 else "MEDIUM" if score <= 60 else "HIGH" if score <= 80 else "CRITICAL"
    return score, level, factors


def authorize(request: ActionRequest) -> PolicyResult:
    agent = AGENTS.get(request.agent_id)
    if agent is None:
        return PolicyResult(Decision.DENY, ["unknown_agent"], 100, "CRITICAL")
    if not agent.active:
        return PolicyResult(Decision.DENY, ["agent_inactive"], 100, "CRITICAL")
    if request.credential_id != agent.credential_id:
        return PolicyResult(Decision.DENY, ["credential_mismatch"], 100, "CRITICAL")
    if request.action not in agent.capabilities:
        return PolicyResult(Decision.DENY, ["capability_not_granted"], 100, "CRITICAL")
    if request.requested_scope > agent.max_scope:
        return PolicyResult(Decision.DENY, ["scope_exceeded"], 90, "CRITICAL")
    if request.requested_scope <= 0:
        return PolicyResult(Decision.DENY, ["empty_scope"], 80, "HIGH")

    score, level, factors = risk_for(request)
    if score >= 80:
        return PolicyResult(Decision.DENY, ["risk_threshold_exceeded", *factors], score, level)
    if score >= 50:
        return PolicyResult(Decision.REQUIRE_APPROVAL, ["human_approval_required", *factors], score, level)
    return PolicyResult(Decision.ALLOW, ["policy_satisfied", *factors], score, level)
