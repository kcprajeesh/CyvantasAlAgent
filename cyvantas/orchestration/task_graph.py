from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class TaskState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class Task:
    id: str
    agent: str
    dependencies: set[str] = field(default_factory=set)
    permissions: set[str] = field(default_factory=set)
    state: TaskState = TaskState.QUEUED
    evidence_ids: list[str] = field(default_factory=list)
    outputs: dict = field(default_factory=dict)


class TaskGraph:
    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}

    def add(self, task: Task) -> None:
        if task.id in self.tasks:
            raise ValueError(f"duplicate task id: {task.id}")
        unknown = task.dependencies - self.tasks.keys()
        if unknown:
            raise ValueError(f"unknown dependencies: {sorted(unknown)}")
        self.tasks[task.id] = task

    def ready(self) -> list[Task]:
        return [
            task for task in self.tasks.values()
            if task.state == TaskState.QUEUED and all(self.tasks[d].state == TaskState.COMPLETE for d in task.dependencies)
        ]
