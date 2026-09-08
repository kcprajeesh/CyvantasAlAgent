from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class FindingStatus(StrEnum):
    CANDIDATE = "candidate"
    INVESTIGATING = "investigating"
    VALIDATED = "validated"
    PARTIALLY_VALIDATED = "partially_validated"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"
    ACCEPTED = "accepted"
    REPORTED = "reported"
    RESOLVED = "resolved"


@dataclass
class Finding:
    engagement_id: str
    title: str
    category: str
    severity: str = "informational"
    confidence: float = 0.0
    status: FindingStatus = FindingStatus.CANDIDATE
    asset: str = ""
    endpoint: str = ""
    method: str = ""
    parameter: str = ""
    description: str = ""
    impact: str = ""
    preconditions: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    request_ids: list[str] = field(default_factory=list)
    response_ids: list[str] = field(default_factory=list)
    poc_ids: list[str] = field(default_factory=list)
    source_agents: list[str] = field(default_factory=list)
    duplicate_candidates: list[str] = field(default_factory=list)
    validation: dict[str, Any] = field(default_factory=dict)
    scope_decision: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: f"finding_{uuid4().hex[:12]}")
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data
