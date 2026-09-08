from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EngagementType(StrEnum):
    BUG_BOUNTY = "bug_bounty"
    PENTEST = "pentest"
    INTERNAL = "internal"
    LAB = "lab"
    CTF = "ctf"


@dataclass
class Engagement:
    id: str
    name: str
    owner: str = ""
    type: EngagementType = EngagementType.PENTEST
    authorization_confirmed: bool = False
    authorization_evidence: str = ""
    domains: list[str] = field(default_factory=list)
    subdomains: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    ip_ranges: list[str] = field(default_factory=list)
    repositories: list[str] = field(default_factory=list)
    applications: list[str] = field(default_factory=list)
    exclusions: dict[str, list[str]] = field(default_factory=dict)
    rate_limits: dict[str, int | float] = field(default_factory=dict)
    execution: dict[str, bool] = field(default_factory=lambda: {
        "allow_network": False, "allow_browser": False, "allow_commands": False,
    })
    budgets: dict[str, int | float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def ready_for_testing(self) -> bool:
        return self.authorization_confirmed and bool(
            self.domains or self.subdomains or self.urls or self.ip_ranges or self.repositories or self.applications
        )
