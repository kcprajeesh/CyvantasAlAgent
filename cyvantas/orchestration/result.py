from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    status: str
    observations: list[dict[str, Any]] = field(default_factory=list)
    candidate_findings: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    recommended_next_tasks: list[str] = field(default_factory=list)
    confidence: float = 0.0
    errors: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
