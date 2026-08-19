from dataclasses import dataclass
from uuid import uuid4

@dataclass(frozen=True)
class ExecutionResult:
    execution_id: str
    status: str
    verified: bool
    output: dict


def execute_sandbox_action(action: str, resource: str, scope: int) -> ExecutionResult:
    execution_id = str(uuid4())
    # Deliberately synthetic: no external side effect in the hackathon demo.
    output = {"action": action, "resource": resource, "scope": scope, "simulated": True}
    return ExecutionResult(execution_id, "EXECUTED", True, output)
