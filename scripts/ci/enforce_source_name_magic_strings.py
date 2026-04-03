from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from scripts.ci.git_diff import build_added_lines_map
from scripts.ci.reporting import split_csv

SOURCE_LITERAL_RE = re.compile(r"['\"]([a-z0-9_]+\.json)['\"]")
UPPER_CONSTANT_ASSIGN_RE = re.compile(r"^\s*[A-Z][A-Z0-9_]*\s*=\s*['\"][a-z0-9_]+\.json['\"]\s*$")
ALLOWED_PATHS = (
    "tests/",
)
ALLOWED_FILES = {
    "layers/zero/source_names.py",
}


def _is_allowed(file_path: str, line: str) -> bool:
    if file_path in ALLOWED_FILES:
        return True
    if any(file_path.startswith(prefix) for prefix in ALLOWED_PATHS):
        return True
    return bool(UPPER_CONSTANT_ASSIGN_RE.match(line))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect newly added magic string source names (*.json literals)."
    )
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--changed-files", default="")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    changed_files = [f for f in split_csv(args.changed_files) if f.endswith(".py")]
    if not changed_files:
        print("Brak zmienionych plików Python; magic-string gate pominięty.")
        return 0

    added_lines_map = build_added_lines_map(args.base_sha, args.head_sha, changed_files)
    if not added_lines_map:
        print("Brak diffu dodanych linii; magic-string gate pominięty.")
        return 0

    violations: list[str] = []
    for file_path in changed_files:
        path = Path(file_path)
        if not path.exists():
            continue
        file_lines = path.read_text(encoding="utf-8").splitlines()

        for line_no in sorted(added_lines_map.get(file_path, set())):
            if line_no <= 0 or line_no > len(file_lines):
                continue
            line = file_lines[line_no - 1]
            if not SOURCE_LITERAL_RE.search(line):
                continue
            if _is_allowed(file_path, line):
                continue
            violations.append(f"{file_path}:{line_no} -> {line.strip()}")

    if not violations:
        print("Brak nowych magic stringów źródeł: OK")
        return 0

    print("::error::Wykryto nowe magic stringi nazw źródeł (*.json):")
    for violation in violations:
        print(f" - {violation}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
