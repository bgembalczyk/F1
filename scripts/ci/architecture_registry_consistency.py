#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from scripts.ci.reporting import CiReport
from scripts.ci.reporting import CiStatus
from scripts.ci.reporting import print_console_report
from tests.architecture.rules import DOMAINS
from tests.architecture.rules import ENTRYPOINT_DOMAINS

IGNORED_PACKAGES = {"base", "wiki", "__pycache__"}


def _discovered_domains() -> set[str]:
    root = Path("scrapers")
    return {
        path.name
        for path in root.iterdir()
        if path.is_dir() and path.name not in IGNORED_PACKAGES
    }


def _discovered_entrypoint_domains() -> set[str]:
    root = Path("scrapers")
    return {
        path.name
        for path in root.iterdir()
        if path.is_dir() and (path / "entrypoint.py").exists()
    }


def main() -> int:
    details: list[str] = []
    discovered_domains = _discovered_domains()
    discovered_entrypoint_domains = _discovered_entrypoint_domains()

    if discovered_domains != set(DOMAINS):
        details.append(
            "DOMAINS mismatch: "
            f"discovered={sorted(discovered_domains)} configured={sorted(DOMAINS)}"
        )

    if discovered_entrypoint_domains != set(ENTRYPOINT_DOMAINS):
        details.append(
            "ENTRYPOINT_DOMAINS mismatch: "
            f"discovered={sorted(discovered_entrypoint_domains)} configured={sorted(ENTRYPOINT_DOMAINS)}"
        )

    status = CiStatus.ok if not details else CiStatus.fail
    summary = (
        "Rejestr architektury jest spójny z aktualnymi pakietami."
        if not details
        else "Rejestr architektury nie jest spójny z kodem."
    )
    report = CiReport(
        check_name="architecture-registry",
        status=status,
        summary=summary,
        recommendation="Zsynchronizuj tests/architecture/rules.py z aktualną strukturą scrapers/*.",
        details=tuple(details),
    )
    print_console_report(report)
    return 0 if status == CiStatus.ok else 1


if __name__ == "__main__":
    sys.exit(main())
