from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class EvidenceArtifact:
    engagement_id: str
    type: str
    storage_path: str
    sha256: str
    source: str = ""
    target: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    sanitized: bool = True
    id: str = field(default_factory=lambda: f"evidence_{uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
