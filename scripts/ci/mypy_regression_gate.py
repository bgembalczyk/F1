#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SUMMARY_PATTERN = re.compile(r"Found\s+(\d+)\s+errors?")
GIT_BIN = shutil.which("git") or "git"


def _run_mypy(repo_dir: Path) -> tuple[int, str]:
    # nosec B603 -- uruchomienie zaufanego `python -m mypy`
    proc = subprocess.run(
        [sys.executable, "-m", "mypy", "--config-file", "mypy.ini"],
        cwd=repo_dir,
        text=True,
        capture_output=True,
        check=False,
    )
    output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    if "Success: no issues found" in output:
        return 0, output.strip()
    match = SUMMARY_PATTERN.search(output)
    if match:
        return int(match.group(1)), output.strip()
    return 10**9, output.strip()


def _git(*args: str) -> None:
    # nosec B603 -- zaufane wywołanie lokalnego `git`
    subprocess.run(
        [GIT_BIN, *args],
        check=True,
        text=True,
        capture_output=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CI gate: nie pozwalaj zwiększać liczby błędów typowania (mypy).",
    )
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument(
        "--error-budget",
        type=int,
        default=None,
        help="Maksymalna akceptowalna liczba błędów mypy dla head.",
    )
    args = parser.parse_args()

    repo_root = Path.cwd()

    with tempfile.TemporaryDirectory(prefix="mypy-base-") as temp_dir:
        base_worktree = Path(temp_dir) / "base"
        _git("worktree", "add", "--detach", str(base_worktree), args.base_sha)
        try:
            base_errors, base_output = _run_mypy(base_worktree)
        finally:
            # nosec B603 -- zaufane wywołanie lokalnego `git worktree remove`
            subprocess.run(
                [GIT_BIN, "worktree", "remove", "--force", str(base_worktree)],
                check=False,
                capture_output=True,
                text=True,
            )

    head_errors, head_output = _run_mypy(repo_root)

    print(f"Mypy errors (base {args.base_sha[:7]}): {base_errors}")
    print(f"Mypy errors (head {args.head_sha[:7]}): {head_errors}")

    if head_errors > base_errors:
        print("\n=== BASE OUTPUT ===")
        print(base_output)
        print("\n=== HEAD OUTPUT ===")
        print(head_output)
        print("\nRegresja typowania: liczba błędów wzrosła.")
        return 1

    if args.error_budget is not None and head_errors > args.error_budget:
        print(
            f"Przekroczony budżet błędów mypy: {head_errors} > {args.error_budget}.",
        )
        print("\n=== HEAD OUTPUT ===")
        print(head_output)
        return 1

    print("Brak regresji typowania (liczba błędów nie wzrosła).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
