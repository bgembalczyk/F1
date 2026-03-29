from __future__ import annotations

from pathlib import Path
from typing import Callable

from scripts.ci.reporting import CiReport
from scripts.ci.reporting import CiStatus
from scripts.ci.reporting import print_console_report

CheckRunner = Callable[[], list[str]]


def iter_python_paths(paths: list[Path]) -> list[Path]:
    """Collect all Python files from explicit files/directories."""
    python_paths: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            python_paths.append(path)
            continue
        if path.is_dir():
            python_paths.extend(path.rglob("*.py"))
    return python_paths


def run_cli(check_name: str, run_check: CheckRunner, recommendation: str) -> int:
    """Execute `run_check()` and report result in a unified format."""
    errors = run_check()
    status = CiStatus.ok if not errors else CiStatus.fail
    summary = "Brak naruszeń." if not errors else f"Wykryto {len(errors)} naruszeń."
    report = CiReport(
        check_name=check_name,
        status=status,
        summary=summary,
        recommendation=recommendation,
        details=tuple(errors),
    )
    print_console_report(report)
    return 0 if status == CiStatus.ok else 1
