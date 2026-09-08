from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CyvantasConfig:
    workspace: Path = Path(".cyvantas")
    autonomous_level: int = 1
    allow_network: bool = False
    allow_browser: bool = False
    allow_commands: bool = False
    budgets: dict[str, int | float] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not 0 <= self.autonomous_level <= 4:
            raise ValueError("autonomous_level must be between 0 and 4")
        for key in ("max_tokens", "max_requests", "max_concurrent_agents", "max_browser_sessions", "max_command_executions"):
            value = self.budgets.get(key)
            if value is not None and value < 0:
                raise ValueError(f"{key} cannot be negative")
