from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from scripts.ci.git_diff import build_added_lines_map
from scripts.ci.git_diff import list_changed_files

if TYPE_CHECKING:
    from collections.abc import Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
BLOCKED_IMPORT_SOURCES = frozenset(
    {"scrapers.config", "scrapers.config_table", "scrapers.base.table.config"},
)


@dataclass(frozen=True)
class Violation:
    path: str
    line: int
    message: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Blokuje nowe importy aliasu `ScraperConfig`; "
            "użyj `RuntimeConfig` albo `TableConfig`."
        ),
    )
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    return parser.parse_args(argv)


def collect_alias_import_violations(
    *,
    added_lines_map: dict[str, set[int]],
) -> list[Violation]:
    violations: list[Violation] = []
    for rel_path, added_lines in sorted(added_lines_map.items()):
        if not rel_path.endswith(".py"):
            continue
        file_path = REPO_ROOT / rel_path
        if not file_path.exists():
            continue
        source = file_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.lineno not in added_lines or node.module is None:
                continue
            if node.module not in BLOCKED_IMPORT_SOURCES:
                continue
            for imported in node.names:
                if imported.name != "ScraperConfig":
                    continue
                violations.append(
                    Violation(
                        path=rel_path,
                        line=node.lineno,
                        message=(
                            "Zakaz nowego importu aliasu `ScraperConfig`. "
                            "Użyj `RuntimeConfig` lub `TableConfig` z "
                            "`scrapers.configs.public`."
                        ),
                    ),
                )
    return violations


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(list(argv) if argv is not None else sys.argv[1:])
    changed_files = list_changed_files(args.base_sha, args.head_sha)
    if not changed_files:
        print("Brak zmienionych plików do walidacji importów ScraperConfig.")
        return 0
    added_lines_map = build_added_lines_map(
        args.base_sha,
        args.head_sha,
        changed_files,
    )
    violations = collect_alias_import_violations(added_lines_map=added_lines_map)
    if not violations:
        print("Walidacja importów ScraperConfig zakończona sukcesem.")
        return 0

    for violation in violations:
        print(f"::error::{violation.format()}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
