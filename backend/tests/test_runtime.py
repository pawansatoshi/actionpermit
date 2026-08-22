from app.runtime import execute_sandbox_action


def test_executor_rejects_unregistered_action_without_side_effect():
    result = execute_sandbox_action("invoice.delete", "invoices", 1)
    assert result.status == "REJECTED"
    assert result.verified is False
    assert result.output["reason"] == "executor_capability_not_registered"


def test_executor_rejects_arbitrary_resource():
    result = execute_sandbox_action("invoice.read", "../../etc/passwd", 1)
    assert result.status == "REJECTED"
    assert result.verified is False


def test_executor_rejects_path_like_resource():
    result = execute_sandbox_action("invoice.read", "/tmp/invoices", 1)
    assert result.status == "REJECTED"
    assert result.verified is False
