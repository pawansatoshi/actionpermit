import json
import os
from uuid import uuid4
from fastapi import APIRouter, Header, HTTPException
from .models import ActionRequest, DecisionResponse
from .policy import authorize
from .runtime import execute_sandbox_action

router = APIRouter(prefix="/api/v1", tags=["action"])
EVIDENCE: dict[str, dict] = {}
REQUESTS: dict[str, DecisionResponse] = {}


def _reason_with_gemini(request: ActionRequest, decision: str, reasons: list[str]) -> str | None:
    if not os.getenv("GEMINI_API_KEY"):
        return None
    try:
        from google import genai
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        prompt = json.dumps({
            "task": "Explain this authorization decision in one concise paragraph. Do not alter it.",
            "request": request.model_dump(),
            "deterministic_decision": decision,
            "policy_reasons": reasons,
        })
        response = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"), contents=prompt)
        return response.text[:1000] if response.text else None
    except Exception:
        # AI reasoning is advisory. A model outage never changes authorization.
        return None

@router.post("/decisions", response_model=DecisionResponse)
def decide(request: ActionRequest, x_request_id: str | None = Header(default=None)) -> DecisionResponse:
    if x_request_id and x_request_id != request.request_id:
        raise HTTPException(status_code=400, detail="request_id_mismatch")
    existing = REQUESTS.get(request.request_id)
    if existing is not None:
        return existing

    decision, reasons = authorize(request)
    execution_id = None
    verified = False
    execution_output = None
    if decision.value == "ALLOW":
        result = execute_sandbox_action(request.action, request.resource, request.requested_scope)
        execution_id = result.execution_id
        verified = result.verified
        execution_output = result.output
        if not verified:
            decision = type(decision).DENY
            reasons = ["execution_verification_failed"]
            execution_id = None

    evidence_id = str(uuid4())
    reasoning = _reason_with_gemini(request, decision.value, reasons)
    response = DecisionResponse(request_id=request.request_id, decision=decision, reasons=reasons, execution_id=execution_id, evidence_id=evidence_id, agent_reasoning=reasoning)
    REQUESTS[request.request_id] = response
    EVIDENCE[evidence_id] = {
        "request_id": request.request_id,
        "decision": decision.value,
        "reasons": reasons,
        "execution_id": execution_id,
        "verified": verified,
        "execution_output": execution_output,
    }
    return response

@router.get("/audit/{evidence_id}")
def audit(evidence_id: str) -> dict:
    item = EVIDENCE.get(evidence_id)
    if item is None:
        raise HTTPException(status_code=404, detail="evidence_not_found")
    return item
