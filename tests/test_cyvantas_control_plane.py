from pathlib import Path

import pytest

from cyvantas.core.orchestrator import CyvantasOrchestrator, EngagementStatus
from cyvantas.execution.broker import ExecutionBroker
from cyvantas.models.finding import Finding
from cyvantas.orchestration.task_graph import Task, TaskGraph, TaskState
from cyvantas.security.approval import ApprovalEngine
from cyvantas.security.network import NetworkPolicy
from cyvantas.security.policy import PolicyContext, PolicyDecision, PolicyEngine
from cyvantas.security.scope import ScopeEngine, ScopeRule
from cyvantas.security.secrets import SecretRedactor
from cyvantas.security.workspace import PathGuard, PathPolicyError
from cyvantas.storage.evidence import EvidenceStore


def test_policy_fails_closed_without_authorization():
    result = PolicyEngine().evaluate(PolicyContext("e", "a", "READ_TARGET", "example.com", permissions=frozenset({"READ_TARGET"})))
    assert result.decision is PolicyDecision.DENY


def test_scope_deny_wins():
    scope = ScopeEngine([ScopeRule("example.com"), ScopeRule("admin.example.com", allow=False)])
    assert scope.check("https://example.com").allowed
    assert not scope.check("https://admin.example.com").allowed


def test_private_and_localhost_blocked():
    scope = ScopeEngine([ScopeRule("127.0.0.1", kind="ip"), ScopeRule("example.com")])
    policy = NetworkPolicy(scope)
    assert not policy.check_url("http://127.0.0.1/").allowed
    assert not policy.check_url("http://10.0.0.1/").allowed


def test_workspace_traversal_and_sensitive_paths(tmp_path: Path):
    guard = PathGuard(tmp_path / ".cyvantas")
    with pytest.raises(PathPolicyError):
        guard.resolve("../../etc/passwd")
    with pytest.raises(PathPolicyError):
        guard.validate_read(".env")


def test_symlink_escape_blocked(tmp_path: Path):
    ws = tmp_path / ".cyvantas"
    guard = PathGuard(ws)
    outside = tmp_path / "outside"
    outside.mkdir()
    (ws / "link").symlink_to(outside, target_is_directory=True)
    with pytest.raises(PathPolicyError):
        guard.validate_read("link")


def test_secret_redaction():
    out = SecretRedactor().redact("Authorization: Bearer abcdefghijklmnop\npassword=supersecret")
    assert out.redactions >= 2
    assert "supersecret" not in out.text


def test_evidence_hash_and_tamper_detection(tmp_path: Path):
    store = EvidenceStore(tmp_path / ".cyvantas")
    artifact = store.put_text("e", "http_response", "hello")
    assert store.verify(artifact)
    path = store.guard.resolve(artifact.storage_path)
    path.write_text("tampered")
    assert not store.verify(artifact)


def test_approval_is_bound_to_report_version():
    engine = ApprovalEngine(b"unit-test-secret")
    token = engine.issue("e", "f", "v1", "hackerone")
    assert engine.verify(token, "e", "f", "v1", "hackerone")
    assert not engine.verify(token, "e", "f", "v2", "hackerone")


def test_task_graph_ready_and_pause_cancel():
    graph = TaskGraph()
    graph.add(Task("a", "recon"))
    graph.add(Task("b", "hunter", dependencies={"a"}))
    assert [t.id for t in graph.ready()] == ["a"]
    graph.tasks["a"].state = TaskState.COMPLETE
    assert [t.id for t in graph.ready()] == ["b"]
    orch = CyvantasOrchestrator(graph)
    orch.pause()
    assert orch.state.status is EngagementStatus.PAUSED
    assert orch.ready_tasks() == []


def test_finding_rejects_invalid_confidence():
    with pytest.raises(ValueError):
        Finding("e", "x", "x", confidence=1.1)
