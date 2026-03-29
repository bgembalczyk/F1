"""Shared rules and checks for known module typo detection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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


def _validate_target_packages(typo_rules: tuple[TypoRule, ...] = TYPO_RULES) -> list[str]:
    errors: list[str] = []
    for rule in typo_rules:
        for package in rule.target_packages:
            expected = package / rule.expected_module_name
            typo = package / rule.disallowed_typo_name

            if not expected.exists():
                errors.append(f"missing expected module: {expected}")
            if typo.exists():
                errors.append(f"found typo module: {typo}")
    return errors


def _scan_typo_imports(typo_rules: tuple[TypoRule, ...] = TYPO_RULES) -> list[str]:
    errors: list[str] = []
    for source_dir in SOURCE_DIRS:
        root = PROJECT_ROOT / source_dir
        if not root.exists():
            continue
        for py_file in root.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            for rule in typo_rules:
                if rule.disallowed_import in content:
                    rel_path = py_file.relative_to(PROJECT_ROOT)
                    errors.append(f"found typo import in {rel_path}")
    return errors


def run_known_typos_check() -> list[str]:
    return [
        *_validate_target_packages(),
        *_scan_typo_imports(),
    ]
