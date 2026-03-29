#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from scripts.ci.reporting import CiReport
from scripts.ci.reporting import CiStatus
from scripts.ci.reporting import print_console_report

SCOPE_PREFIXES = ("layers/", "validation/", "infrastructure/http_client/")


def _git(*args: str) -> str:
    res = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return res.stdout


def _scope_files(repo_dir: Path) -> list[str]:
    output = _git("ls-files", "*.py")
    return [line for line in output.splitlines() if line.startswith(SCOPE_PREFIXES)]


def _run_mypy(repo_dir: Path, files: list[str]) -> tuple[int, str]:
    if not files:
        return 0, "Brak plików w scope mypy."
    proc = subprocess.run(
        ["mypy", "--config-file", "mypy.ini", *files],
        cwd=repo_dir,
        check=False,
        capture_output=True,
        text=True,
    )
    output = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    errors = 0
    for line in output.splitlines():
        if ": error:" in line:
            errors += 1
    return errors, output


def main() -> int:
    parser = argparse.ArgumentParser(description="Regression gate for selected mypy scope.")
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    args = parser.parse_args()

    repo_root = Path.cwd()
    scope_files = _scope_files(repo_root)

    with tempfile.TemporaryDirectory(prefix="mypy-scope-base-") as temp_dir:
        base_worktree = Path(temp_dir) / "base"
        subprocess.run(["git", "worktree", "add", "--detach", str(base_worktree), args.base_sha], check=True)
        try:
            base_errors, _ = _run_mypy(base_worktree, scope_files)
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(base_worktree)], check=False)

    head_errors, head_output = _run_mypy(repo_root, scope_files)

    status = CiStatus.ok if head_errors <= base_errors else CiStatus.fail
    summary = (
        f"Mypy scope regression: base={base_errors}, head={head_errors}."
    )
    details: tuple[str, ...] = ()
    if status == CiStatus.fail:
        details = tuple(head_output.splitlines()[:20])

    report = CiReport(
        check_name="mypy-scope-regression",
        status=status,
        summary=summary,
        recommendation="Usuń nowe błędy typowania w zakresie rolloutu lub popraw anotacje.",
        details=details,
    )
    print_console_report(report)
    return 0 if status == CiStatus.ok else 1


if __name__ == "__main__":
    sys.exit(main())
