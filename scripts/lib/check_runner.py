from __future__ import annotations

from pathlib import Path
from typing import Callable

CheckRunner = Callable[[], list[str]]


def parse_target_paths(
    argv: list[str],
    *,
    default_paths: list[Path],
    repo_root: Path | None = None,
) -> tuple[list[Path], list[str]]:
    """Parse optional `--paths` from argv.

    Returns a tuple: (resolved_target_paths, remaining_args).
    If `--paths` is omitted, `default_paths` are returned.
    If `--paths` is present without values, an explicit empty list is returned.
    """
    remaining_args: list[str] = []
    parsed_path_args: list[str] | None = None

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg != "--paths":
            remaining_args.append(arg)
            i += 1
            continue

        parsed_path_args = []
        i += 1
        while i < len(argv) and not argv[i].startswith("--"):
            parsed_path_args.append(argv[i])
            i += 1

    if parsed_path_args is None:
        return default_paths, remaining_args

    base = repo_root or Path.cwd()
    return [base / raw_path for raw_path in parsed_path_args], remaining_args


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
