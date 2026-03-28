#!/usr/bin/env python3
"""Static check for known module/file typos in key packages."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = (
    "layers",
    "scrapers",
    "models",
    "infrastructure",
    "validation",
    "complete_extractor",
)

TARGET_PACKAGES = (
    PROJECT_ROOT / "scrapers" / "wiki",
    PROJECT_ROOT / "scrapers" / "wiki" / "parsers" / "sections",
)

EXPECTED_MODULE_NAME = "constants.py"
DISALLOWED_TYPO_NAME = "contants.py"
DISALLOWED_IMPORT = "scrapers.wiki.contants"


def _validate_target_packages() -> list[str]:
    errors: list[str] = []
    for package in TARGET_PACKAGES:
        expected = package / EXPECTED_MODULE_NAME
        typo = package / DISALLOWED_TYPO_NAME

        if not expected.exists():
            errors.append(f"missing expected module: {expected}")
        if typo.exists():
            errors.append(f"found typo module: {typo}")
    return errors


def _scan_typo_imports() -> list[str]:
    errors: list[str] = []
    for source_dir in SOURCE_DIRS:
        root = PROJECT_ROOT / source_dir
        if not root.exists():
            continue
        for py_file in root.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            if DISALLOWED_IMPORT in content:
                rel_path = py_file.relative_to(PROJECT_ROOT)
                errors.append(f"found typo import in {rel_path}")
    return errors


def main() -> int:
    errors = [
        *_validate_target_packages(),
        *_scan_typo_imports(),
    ]

    if not errors:
        print("OK: no known module typos detected.")
        return 0

    print("Known module typo check failed:")
    for error in errors:
        print(f"- {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
