from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from cyvantas.orchestration.task_graph import TaskGraph, TaskState
from cyvantas.security.policy import PolicyDecision


class EngagementStatus(StrEnum):
    INITIALIZING = "INITIALIZING"
    AUTHORIZATION_REQUIRED = "AUTHORIZATION_REQUIRED"
    SCOPE_REQUIRED = "SCOPE_REQUIRED"
    READY = "READY"
    RECON = "RECON"
    MAPPING = "MAPPING"
    HUNTING = "HUNTING"
    VALIDATING = "VALIDATING"
    CORRELATING = "CORRELATING"
    CHAINING = "CHAINING"
    REPORTING = "REPORTING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    SUBMITTING = "SUBMITTING"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class OrchestratorState:
    status: EngagementStatus = EngagementStatus.INITIALIZING
    paused: bool = False
    cancelled: bool = False


class CyvantasOrchestrator:
    """Stateful control-plane shell for deterministic task scheduling."""

    def __init__(self, task_graph: TaskGraph | None = None) -> None:
        self.graph = task_graph or TaskGraph()
        self.state = OrchestratorState()

    def pause(self) -> None:
        self.state.paused = True
        self.state.status = EngagementStatus.PAUSED
        for task in self.graph.tasks.values():
            if task.state == TaskState.RUNNING:
                task.state = TaskState.PAUSED

    def cancel(self) -> None:
        self.state.cancelled = True
        self.state.status = EngagementStatus.CANCELLED
        for task in self.graph.tasks.values():
            if task.state in {TaskState.QUEUED, TaskState.RUNNING, TaskState.PAUSED}:
                task.state = TaskState.CANCELLED

    def ready_tasks(self):
        if self.state.paused or self.state.cancelled:
            return []
        return self.graph.ready()
