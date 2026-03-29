#!/usr/bin/env python3
"""Static check for known module/file typos in key packages."""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from pathlib import Path
import sys
from scripts.lib.known_typos import run_known_typos_check

_BOOTSTRAP_PATH = Path(__file__).resolve().parent / "lib" / "bootstrap.py"
_BOOTSTRAP_SPEC = importlib.util.spec_from_file_location(
    "_scripts_bootstrap",
    _BOOTSTRAP_PATH,
)
assert _BOOTSTRAP_SPEC and _BOOTSTRAP_SPEC.loader
_BOOTSTRAP_MODULE = importlib.util.module_from_spec(_BOOTSTRAP_SPEC)
_BOOTSTRAP_SPEC.loader.exec_module(_BOOTSTRAP_MODULE)

PROJECT_ROOT = _BOOTSTRAP_MODULE.ensure_project_root_on_path()

from scripts.lib.check_runner import run_cli

SOURCE_DIRS = (
    "layers",
    "scrapers",
    "models",
    "infrastructure",
    "validation",
    "complete_extractor",
)


@dataclass(frozen=True)
class TypoRule:
    target_packages: tuple[Path, ...]
    expected_module_name: str
    disallowed_typo_name: str
    disallowed_import: str


TYPO_RULES: tuple[TypoRule, ...] = (
    TypoRule(
        target_packages=(
            PROJECT_ROOT / "scrapers" / "wiki",
            PROJECT_ROOT / "scrapers" / "wiki" / "parsers" / "sections",
        ),
        expected_module_name="constants.py",
        disallowed_typo_name="contants.py",
        disallowed_import="scrapers.wiki.contants",
    ),
    TypoRule(
        target_packages=(
            PROJECT_ROOT / "scrapers" / "base" / "orchestration" / "components",
        ),
        expected_module_name="section_source_adapter.py",
        disallowed_typo_name="section_soruce_adapter.py",
        disallowed_import="scrapers.base.orchestration.components.section_soruce_adapter",
    ),
)


def _validate_target_packages() -> list[str]:
    errors: list[str] = []
    for rule in TYPO_RULES:
        for package in rule.target_packages:
            expected = package / rule.expected_module_name
            typo = package / rule.disallowed_typo_name

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
            for rule in TYPO_RULES:
                if rule.disallowed_import in content:
                    rel_path = py_file.relative_to(PROJECT_ROOT)
                    errors.append(f"found typo import in {rel_path}")
    return errors


def run_check() -> list[str]:
    return run_known_typos_check(PROJECT_ROOT)


def main(argv: list[str] | None = None) -> int:
    del argv
    return run_cli("known-module-typos", run_check)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
