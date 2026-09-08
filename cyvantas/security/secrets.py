from __future__ import annotations

import re
from dataclasses import dataclass


_PATTERNS = [
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"(?i)(api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*['\"]?[^\s'\"]{8,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)cookie\s*:\s*[^\r\n]+"),
]


@dataclass(frozen=True)
class RedactionResult:
    text: str
    redactions: int


class SecretRedactor:
    def redact(self, text: str) -> RedactionResult:
        count = 0
        output = text
        for pattern in _PATTERNS:
            output, n = pattern.subn("[REDACTED]", output)
            count += n
        return RedactionResult(output, count)


class SecretDetector:
    def contains_secret(self, text: str) -> bool:
        return any(pattern.search(text) for pattern in _PATTERNS)
