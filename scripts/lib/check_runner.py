from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

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


def print_report(check_name: str, errors: list[str]) -> int:
    """Print a unified check report and return process exit code."""
    if not errors:
        print(f"[{check_name}] OK")
        return 0

    print(f"[{check_name}] ERROR")
    for error in errors:
        print(f"- {error}")
    return 1


def run_cli(check_name: str, run_check: CheckRunner) -> int:
    """Execute `run_check()` and report result in a unified format."""
    errors = run_check()
    return print_report(check_name, errors)
