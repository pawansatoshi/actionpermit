from datetime import datetime, timezone
from hashlib import sha256
import json
from uuid import uuid4
from fastapi import APIRouter, Header, HTTPException
from .agent import reason_about
from .models import ActionRequest, DecisionResponse, Decision, Lifecycle, ApprovalRequest
from .policy import authorize, PolicyResult
from .runtime import execute_sandbox_action

router = APIRouter(prefix="/api/v1", tags=["action"])
EVIDENCE: dict[str, dict] = {}
REQUESTS: dict[str, DecisionResponse] = {}
APPROVALS: dict[str, dict] = {}
EVENTS: list[dict] = []


def _event(event: str, request_id: str, **data):
    EVENTS.append({"event": event, "request_id": request_id, "timestamp": datetime.now(timezone.utc).isoformat(), **data})


def _request_fingerprint(request: ActionRequest) -> str:
    payload = json.dumps(request.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def _execute(request: ActionRequest, response: DecisionResponse) -> DecisionResponse:
    _event("EXECUTION_STARTED", request.request_id, evidence_id=response.evidence_id)
    try:
        result = execute_sandbox_action(request.action, request.resource, request.requested_scope)
    except Exception as exc:
        response.lifecycle = Lifecycle.FAILED
        response.decision = Decision.DENY
        response.reasons = ["execution_exception"]
        _event("EXECUTION_FAILED", request.request_id, error=type(exc).__name__)
        return response
    if not result.verified:
        response.lifecycle = Lifecycle.FAILED
        response.decision = Decision.DENY
        response.reasons = ["execution_verification_failed"]
        _event("EXECUTION_FAILED", request.request_id, reason="verification_failed")
        return response
    response.execution_id = result.execution_id
    response.lifecycle = Lifecycle.COMPLETED
    _event("EXECUTION_COMPLETED", request.request_id, execution_id=result.execution_id)
    EVIDENCE[response.evidence_id]["execution_output"] = result.output
    EVIDENCE[response.evidence_id]["verified"] = True
    return response


@router.post("/decisions", response_model=DecisionResponse)
def decide(request: ActionRequest, x_request_id: str | None = Header(default=None)) -> DecisionResponse:
    if x_request_id and x_request_id != request.request_id:
        raise HTTPException(status_code=400, detail="request_id_mismatch")
    existing = REQUESTS.get(request.request_id)
    if existing is not None:
        return existing

    _event("INTENT_RECEIVED", request.request_id, action=request.action)
    try:
        result = authorize(request)
    except Exception as exc:
        result = PolicyResult(Decision.DENY, ["policy_evaluation_failed"], 100, "CRITICAL")
        _event("POLICY_EVALUATION_FAILED", request.request_id, error=type(exc).__name__)
    _event("POLICY_EVALUATED", request.request_id, decision=result.decision.value, risk_score=result.risk_score)
    evidence_id = str(uuid4())
    response = DecisionResponse(request_id=request.request_id, decision=result.decision, lifecycle=Lifecycle.POLICY_EVALUATED, reasons=result.reasons, risk_score=result.risk_score, risk_level=result.risk_level, evidence_id=evidence_id)
    EVIDENCE[evidence_id] = {"request_id": request.request_id, "decision": result.decision.value, "lifecycle": response.lifecycle.value, "reasons": result.reasons, "risk_score": result.risk_score, "risk_level": result.risk_level, "verified": False}

    if result.decision is Decision.ALLOW:
        response.lifecycle = Lifecycle.EXECUTING
        response = _execute(request, response)
    elif result.decision is Decision.REQUIRE_APPROVAL:
        approval_id = str(uuid4())
        response.approval_id = approval_id
        response.lifecycle = Lifecycle.APPROVAL_REQUIRED
        APPROVALS[approval_id] = {"request": request, "request_fingerprint": _request_fingerprint(request), "evidence_id": evidence_id, "status": "PENDING", "created_at": datetime.now(timezone.utc).isoformat()}
        _event("APPROVAL_REQUESTED", request.request_id, approval_id=approval_id)
    else:
        response.lifecycle = Lifecycle.DENIED
        _event("ACTION_DENIED", request.request_id, reasons=result.reasons)

    response.agent_reasoning = reason_about(request.model_dump(), response.decision.value, response.reasons)
    REQUESTS[request.request_id] = response
    EVIDENCE[evidence_id].update({"decision": response.decision.value, "lifecycle": response.lifecycle.value, "approval_id": response.approval_id, "execution_id": response.execution_id, "agent_reasoning": response.agent_reasoning})
    return response


@router.post("/approvals/{approval_id}", response_model=DecisionResponse)
def resolve_approval(approval_id: str, approval: ApprovalRequest) -> DecisionResponse:
    item = APPROVALS.get(approval_id)
    if item is None:
        raise HTTPException(status_code=404, detail="approval_not_found")
    if item["status"] != "PENDING":
        raise HTTPException(status_code=409, detail="approval_already_resolved")
    request: ActionRequest = item["request"]
    if item.get("request_fingerprint") != _request_fingerprint(request):
        raise HTTPException(status_code=409, detail="approval_binding_mismatch")
    response = REQUESTS.get(request.request_id)
    if response is None or response.approval_id != approval_id or response.evidence_id != item["evidence_id"]:
        raise HTTPException(status_code=409, detail="approval_binding_mismatch")
    item.update({"status": "APPROVED" if approval.approved else "REJECTED", "approver": approval.approver, "reason": approval.reason})
    if not approval.approved:
        response.decision = Decision.DENY
        response.lifecycle = Lifecycle.DENIED
        response.reasons = ["human_rejected", approval.reason or "approval_rejected"]
        _event("APPROVAL_REJECTED", request.request_id, approval_id=approval_id, approver=approval.approver)
    else:
        response.decision = Decision.ALLOW
        response.lifecycle = Lifecycle.APPROVED
        _event("APPROVAL_GRANTED", request.request_id, approval_id=approval_id, approver=approval.approver)
        response.lifecycle = Lifecycle.EXECUTING
        response = _execute(request, response)
    EVIDENCE[response.evidence_id].update({"decision": response.decision.value, "lifecycle": response.lifecycle.value, "approval_status": item["status"], "approver": approval.approver, "approval_reason": approval.reason, "execution_id": response.execution_id})
    REQUESTS[request.request_id] = response
    return response


@router.get("/audit/{evidence_id}")
def audit(evidence_id: str) -> dict:
    item = EVIDENCE.get(evidence_id)
    if item is None:
        raise HTTPException(status_code=404, detail="evidence_not_found")
    return {**item, "events": [e for e in EVENTS if e["request_id"] == item["request_id"]]}


@router.get("/audit")
def audit_index() -> list[dict]:
    return list(EVIDENCE.values())
