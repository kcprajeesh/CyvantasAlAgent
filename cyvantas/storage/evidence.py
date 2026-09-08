from __future__ import annotations

import hashlib
from pathlib import Path

from cyvantas.models.evidence import EvidenceArtifact
from cyvantas.security.secrets import SecretDetector, SecretRedactor
from cyvantas.security.workspace import PathGuard


class EvidenceIntegrityError(ValueError):
    pass


class EvidenceStore:
    def __init__(self, workspace: Path) -> None:
        self.guard = PathGuard(workspace)
        self.root = self.guard.validate_write("evidence")
        self.root.mkdir(parents=True, exist_ok=True)
        self.redactor = SecretRedactor()
        self.detector = SecretDetector()

    def put_text(self, engagement_id: str, evidence_type: str, text: str, *, source: str = "", target: str = "") -> EvidenceArtifact:
        sanitized = self.redactor.redact(text).text
        path = self.root / f"{hashlib.sha256(sanitized.encode()).hexdigest()}.txt"
        path.write_text(sanitized, encoding="utf-8")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return EvidenceArtifact(engagement_id, evidence_type, str(path.relative_to(self.guard.workspace)), digest, source, target,
                                {"redactions": sanitized != text}, True)

    def verify(self, artifact: EvidenceArtifact) -> bool:
        path = self.guard.validate_read(artifact.storage_path)
        return hashlib.sha256(path.read_bytes()).hexdigest() == artifact.sha256
