from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from urllib.parse import urlparse

from .scope import ScopeEngine


@dataclass(frozen=True)
class NetworkDecision:
    allowed: bool
    reason: str


class NetworkPolicy:
    """Conservative network guard used before any outbound request."""

    def __init__(self, scope: ScopeEngine, *, allow_private: bool = False, allow_metadata: bool = False) -> None:
        self.scope = scope
        self.allow_private = allow_private
        self.allow_metadata = allow_metadata

    def check_url(self, url: str) -> NetworkDecision:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in {"http", "https"}:
            return NetworkDecision(False, "protocol is not allowed")
        if not host:
            return NetworkDecision(False, "URL has no hostname")
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            ip = None
        if ip:
            if ip.is_loopback or ip.is_unspecified or ip.is_link_local:
                return NetworkDecision(False, "localhost/link-local/unspecified address blocked")
            if ip.is_private and not self.allow_private:
                return NetworkDecision(False, "private address blocked by default")
            if not self.allow_metadata and str(ip) in {"169.254.169.254", "100.100.100.200"}:
                return NetworkDecision(False, "cloud metadata address blocked")
        decision = self.scope.check(url)
        return NetworkDecision(decision.allowed, decision.reason)
