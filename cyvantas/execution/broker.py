from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from cyvantas.security.policy import PolicyContext, PolicyDecision, PolicyEngine
from cyvantas.security.secrets import SecretRedactor
from cyvantas.security.workspace import PathGuard


@dataclass(frozen=True)
class ExecutionResult:
    success: bool
    exit_code: int | None
    stdout: str
    stderr: str
    error_code: str | None = None
    policy_violation: bool = False


class ExecutionBroker:
    """Controlled command broker; never exposes a raw shell interface."""

    def __init__(self, workspace: Path, policy: PolicyEngine, *, allow_commands: set[str] | None = None) -> None:
        self.guard = PathGuard(workspace)
        self.policy = policy
        self.allow_commands = allow_commands or set()
        self.redactor = SecretRedactor()

    def run(self, argv: list[str], context: PolicyContext, *, timeout: float = 30.0, cwd: str = ".") -> ExecutionResult:
        if not argv or not argv[0]:
            return ExecutionResult(False, None, "", "", "INVALID_COMMAND")
        if argv[0] not in self.allow_commands:
            return ExecutionResult(False, None, "", "", "COMMAND_NOT_ALLOWED", True)
        decision = self.policy.evaluate(context)
        if decision.decision is not PolicyDecision.ALLOW:
            return ExecutionResult(False, None, "", decision.reason, "POLICY_DENIED", True)
        try:
            workdir = self.guard.resolve(cwd)
            proc = subprocess.run(
                argv, cwd=workdir, shell=False, capture_output=True, text=True,
                timeout=timeout, env={"PATH": "/usr/bin:/bin"}, check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return ExecutionResult(False, None, self.redactor.redact(str(exc.stdout or "")).text,
                                   self.redactor.redact(str(exc.stderr or "")).text, "TIMEOUT")
        except OSError as exc:
            return ExecutionResult(False, None, "", self.redactor.redact(str(exc)).text, "EXECUTION_ERROR")
        stdout = self.redactor.redact(proc.stdout).text
        stderr = self.redactor.redact(proc.stderr).text
        return ExecutionResult(proc.returncode == 0, proc.returncode, stdout, stderr)
