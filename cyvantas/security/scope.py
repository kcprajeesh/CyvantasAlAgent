from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field
from fnmatch import fnmatch
from urllib.parse import urlparse


@dataclass(frozen=True)
class ScopeRule:
    value: str
    kind: str = "domain"
    allow: bool = True
    ports: frozenset[int] = frozenset()
    protocols: frozenset[str] = frozenset()
    path_prefix: str = ""


@dataclass(frozen=True)
class ScopeDecision:
    allowed: bool
    reason: str
    matched_rule: str | None = None


class ScopeEngine:
    """Single centralized matcher. Deny rules always win."""

    def __init__(self, rules: list[ScopeRule] | None = None) -> None:
        self.rules = list(rules or [])

    def add_rule(self, rule: ScopeRule) -> None:
        self.rules.append(rule)

    def check(self, target: str, *, protocol: str | None = None, port: int | None = None) -> ScopeDecision:
        parsed = urlparse(target if "://" in target else f"https://{target}")
        host = (parsed.hostname or target.split("/", 1)[0]).rstrip(".").lower()
        path = parsed.path or "/"
        effective_port = port or parsed.port
        proto = (protocol or parsed.scheme or "https").lower()

        matched_allow: ScopeRule | None = None
        for rule in self.rules:
            if not self._matches(rule, host, path, proto, effective_port):
                continue
            if not rule.allow:
                return ScopeDecision(False, "explicit deny rule matched", rule.value)
            matched_allow = rule

        if matched_allow is None:
            return ScopeDecision(False, "no allow rule matched")
        return ScopeDecision(True, "allow rule matched", matched_allow.value)

    @staticmethod
    def _matches(rule: ScopeRule, host: str, path: str, protocol: str, port: int | None) -> bool:
        if rule.protocols and protocol not in rule.protocols:
            return False
        if rule.ports and (port is None or port not in rule.ports):
            return False
        if rule.path_prefix and not path.startswith(rule.path_prefix):
            return False

        value = rule.value.lower().rstrip(".")
        if rule.kind == "cidr":
            try:
                return ipaddress.ip_address(host) in ipaddress.ip_network(value, strict=False)
            except ValueError:
                return False
        if rule.kind == "ip":
            return host == value
        if rule.kind == "url":
            parsed = urlparse(rule.value)
            return host == (parsed.hostname or "").lower() and path.startswith(parsed.path or "/")
        if value.startswith("*."):
            base = value[2:]
            return host != base and host.endswith("." + base)
        return fnmatch(host, value)
