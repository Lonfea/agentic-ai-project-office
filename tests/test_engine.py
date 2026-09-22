import pytest

from project_office.engine import demo_office


def test_analysis_is_idempotent_and_explainable():
    office = demo_office()
    first = office.analyze("AI-101")
    second = office.analyze("AI-101")
    assert first == second
    assert len(office.audit) == 1
    assert first["priority"]["components"]


def test_human_approval_gate_and_state_policy():
    office = demo_office()
    office.analyze("AI-101")
    office.transition("AI-101", "awaiting_approval", "pmo", "coordinator")
    with pytest.raises(PermissionError):
        office.transition("AI-101", "approved", "strategy-agent", "agent")
    approved = office.transition("AI-101", "approved", "director", "human-approver", "funded")
    assert approved.state == "approved"


def test_invalid_transition_fails_closed():
    office = demo_office()
    with pytest.raises(ValueError, match="invalid transition"):
        office.transition("AI-101", "executing", "user", "coordinator")


def test_hash_chain_detects_tampering():
    office = demo_office()
    office.analyze("AI-101")
    assert office.verify_audit_chain()
    office.audit[0]["actor"] = "tampered"
    assert not office.verify_audit_chain()


def test_report_orders_priorities():
    report = demo_office().executive_report()
    scores = [row["priority_score"] for row in report["ranked_priorities"]]
    assert scores == sorted(scores, reverse=True)

