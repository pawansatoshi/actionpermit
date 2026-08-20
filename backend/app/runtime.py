from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
import json

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
INVOICE_FILE = DATA_DIR / "invoices.json"


@dataclass(frozen=True)
class ExecutionResult:
    execution_id: str
    status: str
    verified: bool
    output: dict


def execute_sandbox_action(action: str, resource: str, scope: int) -> ExecutionResult:
    """Execute only registered demo capabilities; never accept a caller-supplied filesystem path."""
    execution_id = str(uuid4())
    if action == "invoice.read" and resource == "invoices":
        records = json.loads(INVOICE_FILE.read_text(encoding="utf-8"))
        visible = records[:scope]
        output = {"action": action, "resource": resource, "records_returned": len(visible), "records": visible, "simulated": False}
        verified = len(visible) == min(scope, len(records))
        return ExecutionResult(execution_id, "EXECUTED", verified, output)
    return ExecutionResult(execution_id, "REJECTED", False, {"action": action, "resource": resource, "reason": "executor_capability_not_registered"})
