from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Approval:
    engagement_id: str
    finding_id: str
    report_version: str
    platform: str
    token_digest: str
    created_at: str


class ApprovalEngine:
    def __init__(self, secret: bytes | None = None) -> None:
        self._secret = secret or secrets.token_bytes(32)
        self._approvals: dict[str, Approval] = {}

    @staticmethod
    def _payload(engagement_id: str, finding_id: str, report_version: str, platform: str) -> bytes:
        return "|".join((engagement_id, finding_id, report_version, platform)).encode()

    def issue(self, engagement_id: str, finding_id: str, report_version: str, platform: str) -> str:
        payload = self._payload(engagement_id, finding_id, report_version, platform)
        token = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        digest = hashlib.sha256(token.encode()).hexdigest()
        self._approvals[digest] = Approval(
            engagement_id, finding_id, report_version, platform, digest,
            datetime.now(timezone.utc).isoformat(),
        )
        return token

    def verify(self, token: str, engagement_id: str, finding_id: str, report_version: str, platform: str) -> bool:
        payload = self._payload(engagement_id, finding_id, report_version, platform)
        expected = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(token, expected) and hashlib.sha256(token.encode()).hexdigest() in self._approvals
