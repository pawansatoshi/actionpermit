from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class Decision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_CONDITIONS = "ALLOW_WITH_CONDITIONS"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"


class Lifecycle(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATING = "VALIDATING"
    POLICY_EVALUATED = "POLICY_EVALUATED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: str = Field(min_length=8, max_length=128)
    agent_id: str = Field(min_length=1, max_length=128)
    credential_id: str = Field(min_length=1, max_length=128)
    tool: str = Field(min_length=1, max_length=128)
    action: str = Field(min_length=1, max_length=128)
    resource: str = Field(min_length=1, max_length=256)
    requested_scope: int = Field(ge=0, le=100_000)
    context: dict[str, Any] = Field(default_factory=dict)


class DecisionResponse(BaseModel):
    request_id: str
    decision: Decision
    lifecycle: Lifecycle
    reasons: list[str]
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    execution_id: str | None = None
    evidence_id: str
    approval_id: str | None = None
    agent_reasoning: str | None = None


class ApprovalRequest(BaseModel):
    approved: bool
    approver: str = Field(min_length=1, max_length=128)
    reason: str = Field(default="", max_length=500)
