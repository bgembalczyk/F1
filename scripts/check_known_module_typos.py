#!/usr/bin/env python3
"""Static check for known module/file typos in key packages."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib.check_runner import run_cli

SOURCE_DIRS = (
    "layers",
    "scrapers",
    "models",
    "infrastructure",
    "validation",
    "complete_extractor",
)

DISALLOWED_FILENAME_PATTERNS = (
    "contants",
    "soruce",
)


@dataclass(frozen=True)
class TypoRule:
    target_packages: tuple[Path, ...]
    expected_module_name: str


TYPO_RULES = (
    TypoRule(
        target_packages=(
            PROJECT_ROOT / "scrapers" / "wiki",
            PROJECT_ROOT / "scrapers" / "wiki" / "parsers" / "sections",
        ),
        expected_module_name="constants.py",
    ),
    TypoRule(
        target_packages=(
            PROJECT_ROOT / "scrapers" / "base" / "orchestration" / "components",
        ),
        expected_module_name="section_source_adapter.py",
    ),
)


def _contains_disallowed_pattern(value: str) -> bool:
    return any(pattern in value for pattern in DISALLOWED_FILENAME_PATTERNS)


def _validate_target_packages() -> list[str]:
    errors: list[str] = []
    for rule in TYPO_RULES:
        for package in rule.target_packages:
            expected = package / rule.expected_module_name
            if not expected.exists():
                errors.append(f"missing expected module: {expected}")

            for py_file in package.glob("*.py"):
                if _contains_disallowed_pattern(py_file.name):
                    errors.append(f"found typo module: {py_file}")
    return errors


def _scan_typo_imports() -> list[str]:
    errors: list[str] = []
    for source_dir in SOURCE_DIRS:
        root = PROJECT_ROOT / source_dir
        if not root.exists():
            continue
        for py_file in root.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            if not _contains_disallowed_pattern(content):
                continue
            rel_path = py_file.relative_to(PROJECT_ROOT)
            errors.append(f"found typo import in {rel_path}")
    return errors


def run_check() -> list[str]:
    return [
        *_validate_target_packages(),
        *_scan_typo_imports(),
    ]


def main() -> int:
    return run_cli("known-module-typos", run_check)


if __name__ == "__main__":
    raise SystemExit(main())
