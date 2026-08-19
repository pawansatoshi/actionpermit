from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"

class Lifecycle(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATING = "VALIDATING"
    POLICY_EVALUATED = "POLICY_EVALUATED"
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
    execution_id: str | None = None
    evidence_id: str
    agent_reasoning: str | None = None
