from pathlib import Path

import pytest

from cyvantas.models.engagement import Engagement, EngagementType
from cyvantas.orchestration.budget import BudgetState
from cyvantas.orchestration.registry import AgentRegistry, AgentSpec
from cyvantas.orchestration.result import AgentResult
from cyvantas.security.audit import AuditEvent, AuditLog


def test_engagement_requires_authorization_and_target():
    engagement = Engagement("e", "lab", type=EngagementType.LAB)
    assert not engagement.ready_for_testing()
    engagement.authorization_confirmed = True
    engagement.domains.append("example.test")
    assert engagement.ready_for_testing()


def test_registry_is_deterministic_and_rejects_duplicates():
    registry = AgentRegistry()
    registry.register(AgentSpec("recon", "Recon"))
    with pytest.raises(ValueError):
        registry.register(AgentSpec("recon", "Recon"))
    assert registry.get("recon").id == "recon"


def test_budget_pauses_on_exhaustion():
    budget = BudgetState({"max_requests": 2})
    assert budget.consume("max_requests", 2)
    assert not budget.consume("max_requests", 1)
    assert budget.paused


def test_agent_result_contract():
    AgentResult("success", confidence=0.5)
    with pytest.raises(ValueError):
        AgentResult("success", confidence=2)


def test_audit_log_is_jsonl_and_redacts(tmp_path: Path):
    path = tmp_path / "audit.jsonl"
    AuditLog(path).append(AuditEvent("e", "request", result="Bearer abcdefghijklmnop"))
    line = path.read_text().strip()
    assert "Bearer abcdefghijklmnop" not in line
    assert '"engagement_id": "e"' in line
