#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_PREFIX = "scrapers/parsers/"


def merge_base() -> str:
    result = subprocess.run(
        ["git", "merge-base", "origin/main", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or "HEAD~1"


def changed_python_files(base_ref: str) -> list[str]:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=AM",
            base_ref,
            "HEAD",
            "--",
            "*.py",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def added_lines(base_ref: str, path: str) -> set[int]:
    result = subprocess.run(
        ["git", "diff", "--unified=0", base_ref, "HEAD", "--", path],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return set()

    added: set[int] = set()
    current_line = 0
    remaining = 0
    for line in result.stdout.splitlines():
        if line.startswith("@@"):
            # @@ -a,b +c,d @@
            plus = line.split("+", 1)[1].split(" ", 1)[0]
            if "," in plus:
                start, count = plus.split(",", 1)
                current_line = int(start)
                remaining = int(count)
            else:
                current_line = int(plus)
                remaining = 1
            continue
        if remaining <= 0:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            added.add(current_line)
            current_line += 1
            remaining -= 1
        elif line.startswith("-") and not line.startswith("---"):
            continue
        else:
            current_line += 1
            remaining -= 1
    return added


def violations_for_file(path: str, added_lines: set[int]) -> list[str]:
    if path.startswith(CANONICAL_PREFIX):
        return []

    full_path = ROOT / path
    try:
        tree = ast.parse(full_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, SyntaxError):
        return []

    violations: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if not node.name.endswith("Parser"):
            continue
        if node.lineno not in added_lines:
            continue
        violations.append(
            f"{path}:{node.lineno} class {node.name} must live under {CANONICAL_PREFIX}",
        )
    return violations


def main() -> int:
    base_ref = merge_base()
    changed = changed_python_files(base_ref)
    violations: list[str] = []

    for path in changed:
        lines = added_lines(base_ref, path)
        if not lines:
            continue
        violations.extend(violations_for_file(path, lines))

    if violations:
        print("::error::Parser location gate failed:")
        for violation in violations:
            print(f"::error file={violation}")
        return 1

    print("Parser location gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
