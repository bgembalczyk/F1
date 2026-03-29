#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SUMMARY_PATTERN = re.compile(r"Found\s+(\d+)\s+errors?")


def _run_mypy(repo_dir: Path) -> tuple[int, str]:
    proc = subprocess.run(
        ["mypy", "--config-file", "mypy.ini"],
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
    subprocess.run(["git", *args], check=True, text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CI gate: nie pozwalaj zwiększać liczby błędów typowania (mypy)."
    )
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument(
        "--error-budget",
        type=int,
        default=None,
        help="Maksymalna akceptowalna liczba błędów mypy dla head.",
    )
    parser.add_argument(
        "--github-output",
        default="",
        help="Opcjonalna ścieżka do pliku GITHUB_OUTPUT.",
    )
    args = parser.parse_args()

    repo_root = Path.cwd()

    with tempfile.TemporaryDirectory(prefix="mypy-base-") as temp_dir:
        base_worktree = Path(temp_dir) / "base"
        _git("worktree", "add", "--detach", str(base_worktree), args.base_sha)
        try:
            base_errors, base_output = _run_mypy(base_worktree)
        finally:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(base_worktree)],
                check=False,
                capture_output=True,
                text=True,
            )

    head_errors, head_output = _run_mypy(repo_root)

    print(f"Mypy errors (base {args.base_sha[:7]}): {base_errors}")
    print(f"Mypy errors (head {args.head_sha[:7]}): {head_errors}")

    gate_status = "ok"
    gate_message = "Brak regresji typowania."

    if head_errors > base_errors:
        print("\n=== BASE OUTPUT ===")
        print(base_output)
        print("\n=== HEAD OUTPUT ===")
        print(head_output)
        print("\nRegresja typowania: liczba błędów wzrosła.")
        gate_status = "fail"
        gate_message = "Regresja typowania: liczba błędów mypy wzrosła."
    elif args.error_budget is not None and head_errors > args.error_budget:
        print(
            f"Przekroczony budżet błędów mypy: {head_errors} > {args.error_budget}."
        )
        print("\n=== HEAD OUTPUT ===")
        print(head_output)
        gate_status = "fail"
        gate_message = (
            f"Przekroczony budżet błędów mypy: {head_errors} > {args.error_budget}."
        )
    elif head_errors > 0:
        gate_status = "warn"
        gate_message = (
            "Brak regresji względem base, ale w strict scope nadal są błędy mypy."
        )

    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as handle:
            handle.write(f"base_errors={base_errors}\n")
            handle.write(f"head_errors={head_errors}\n")
            handle.write(f"gate_status={gate_status}\n")
            handle.write(f"gate_message={gate_message}\n")

    if gate_status == "fail":
        return 1
    print("Brak regresji typowania (liczba błędów nie wzrosła).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
