from __future__ import annotations

import os
from pathlib import Path


class PathPolicyError(ValueError):
    pass


SENSITIVE_NAMES = {
    ".env", ".env.local", ".env.production", "credentials.json", "id_rsa",
    "id_ed25519", "authorized_keys", "known_hosts",
}
SENSITIVE_PREFIXES = (".aws", ".ssh", ".config", ".gnupg")
SENSITIVE_ROOTS = (Path("/etc"), Path("/proc"), Path("/sys"), Path("/dev"))


class PathGuard:
    """Canonical-path workspace boundary enforcement."""

    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve(strict=False)
        self.workspace.mkdir(parents=True, exist_ok=True)

    def resolve(self, candidate: str | os.PathLike[str], *, must_exist: bool = False) -> Path:
        raw = Path(candidate)
        if raw.is_absolute():
            path = raw.resolve(strict=False)
        else:
            path = (self.workspace / raw).resolve(strict=False)
        try:
            path.relative_to(self.workspace)
        except ValueError as exc:
            raise PathPolicyError("path escapes Cyvantas workspace") from exc
        if must_exist and not path.exists():
            raise PathPolicyError("path does not exist")
        return path

    def validate_write(self, candidate: str | os.PathLike[str]) -> Path:
        path = self.resolve(candidate)
        self._reject_sensitive(path)
        self._reject_symlink_escape(Path(candidate))
        return path

    def validate_read(self, candidate: str | os.PathLike[str], *, allow_sensitive: bool = False) -> Path:
        path = self.resolve(candidate, must_exist=True)
        if not allow_sensitive:
            self._reject_sensitive(path)
        self._reject_symlink_escape(Path(candidate))
        return path

    def _reject_sensitive(self, path: Path) -> None:
        parts = set(path.parts)
        if path.name in SENSITIVE_NAMES or any(prefix in parts for prefix in SENSITIVE_PREFIXES):
            raise PathPolicyError("sensitive path is blocked by default")
        if any(path == root or root in path.parents for root in SENSITIVE_ROOTS):
            raise PathPolicyError("sensitive system path is blocked")

    def _reject_symlink_escape(self, raw: Path) -> None:
        if raw.is_absolute():
            probe = raw
        else:
            probe = self.workspace / raw
        current = self.workspace
        for part in probe.relative_to(self.workspace).parts:
            current = current / part
            if current.is_symlink():
                target = current.resolve(strict=False)
                try:
                    target.relative_to(self.workspace)
                except ValueError as exc:
                    raise PathPolicyError("symlink escapes workspace") from exc
