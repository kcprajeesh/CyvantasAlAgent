from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .secrets import SecretRedactor


@dataclass(frozen=True)
class AuditEvent:
    engagement_id: str
    action: str
    agent_id: str = ""
    task_id: str = ""
    tool: str = ""
    target: str = ""
    scope_decision: str = ""
    policy_decision: str = ""
    result: str = ""
    duration_ms: int | None = None
    resource_usage: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AuditLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.redactor = SecretRedactor()

    def append(self, event: AuditEvent) -> None:
        data = asdict(event)
        safe = self.redactor.redact(json.dumps(data, sort_keys=True)).text
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(safe + "\n")
