from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PolicyDecision(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


@dataclass(frozen=True)
class PolicyContext:
    engagement_id: str
    agent_id: str
    action: str
    target: str = ""
    risk_level: str = "low"
    authorized: bool = False
    in_scope: bool = False
    permissions: frozenset[str] = frozenset()
    requires_approval: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyDecisionResult:
    decision: PolicyDecision
    reason: str
    policy: str
    engagement_id: str
    tool: str
    target: str


class PolicyEngine:
    """Central fail-closed policy evaluator.

    This is intentionally deterministic. Agent prose cannot override this
    layer; callers must present structured execution context.
    """

    def evaluate(self, context: PolicyContext) -> PolicyDecisionResult:
        if not context.authorized:
            return self._deny(context, "engagement authorization is missing")
        if not context.in_scope:
            return self._deny(context, "target is outside the approved scope")
        if context.action and context.action not in context.permissions:
            return self._deny(context, f"missing permission: {context.action}")
        if context.requires_approval or context.risk_level in {"high", "critical", "destructive"}:
            return PolicyDecisionResult(
                PolicyDecision.REQUIRE_APPROVAL,
                "action requires explicit approval",
                "approval_required_policy",
                context.engagement_id,
                context.action,
                context.target,
            )
        return PolicyDecisionResult(
            PolicyDecision.ALLOW,
            "authorization, scope, and permissions satisfied",
            "default_allow_policy",
            context.engagement_id,
            context.action,
            context.target,
        )

    @staticmethod
    def _deny(context: PolicyContext, reason: str) -> PolicyDecisionResult:
        return PolicyDecisionResult(
            PolicyDecision.DENY,
            reason,
            "fail_closed_policy",
            context.engagement_id,
            context.action,
            context.target,
        )
