from __future__ import annotations

import argparse
from pathlib import Path

from cyvantas import __version__
from cyvantas.core.config import CyvantasConfig


def main() -> int:
    parser = argparse.ArgumentParser(prog="cyvantas", description="Cyvantas AI Agent — evidence-driven application security testing")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command")
    init = sub.add_parser("init", help="initialize a Cyvantas workspace")
    init.add_argument("--workspace", type=Path, default=Path(".cyvantas"))
    doctor = sub.add_parser("doctor", help="validate basic local configuration")
    doctor.add_argument("--workspace", type=Path, default=Path(".cyvantas"))
    status = sub.add_parser("status", help="show basic control-plane status")
    status.add_argument("--workspace", type=Path, default=Path(".cyvantas"))
    args = parser.parse_args()
    if args.command == "init":
        args.workspace.mkdir(parents=True, exist_ok=True)
        for name in ("config", "engagement", "scope", "recon", "targets", "findings", "evidence", "poc", "reports", "brain", "logs", "cache", "artifacts", "telemetry", "approvals", "state"):
            (args.workspace / name).mkdir(exist_ok=True)
        print(f"Cyvantas workspace initialized: {args.workspace}")
        return 0
    if args.command == "doctor":
        cfg = CyvantasConfig(workspace=args.workspace)
        cfg.validate()
        print(f"workspace: {'OK' if args.workspace.exists() else 'MISSING'}")
        print(f"python: OK")
        print("policy defaults: fail-closed")
        return 0
    if args.command == "status":
        print(f"CYVANTAS AI AGENT {__version__}")
        print(f"workspace: {args.workspace}")
        print(f"status: {'READY' if args.workspace.exists() else 'NOT_INITIALIZED'}")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
