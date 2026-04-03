from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TypoRule:
    target_packages: tuple[Path, ...]
    expected_module_name: str
    disallowed_typo_name: str
    disallowed_import: str


SOURCE_DIRS: tuple[str, ...] = (
    "layers",
    "scrapers",
    "models",
    "infrastructure",
    "validation",
    "complete_extractor",
)


def build_default_rules(project_root: Path) -> tuple[TypoRule, ...]:
    return (
        TypoRule(
            target_packages=(
                project_root / "scrapers" / "wiki",
                project_root / "scrapers" / "wiki" / "parsers" / "sections",
            ),
            expected_module_name="constants.py",
            disallowed_typo_name="contants.py",
            disallowed_import="scrapers.wiki.contants",
        ),
        TypoRule(
            target_packages=(
                project_root / "scrapers" / "base" / "orchestration" / "components",
            ),
            expected_module_name="section_source_adapter.py",
            disallowed_typo_name="section_soruce_adapter.py",
            disallowed_import=(
                "scrapers.base.orchestration.components.section_soruce_adapter"
            ),
        ),
    )


def validate_target_packages(rules: tuple[TypoRule, ...]) -> list[str]:
    errors: list[str] = []
    for rule in rules:
        for package in rule.target_packages:
            expected = package / rule.expected_module_name
            typo = package / rule.disallowed_typo_name

            if not expected.exists():
                errors.append(f"missing expected module: {expected}")
            if typo.exists():
                errors.append(f"found typo module: {typo}")
    return errors


def scan_typo_imports(
    project_root: Path,
    rules: tuple[TypoRule, ...],
    source_dirs: tuple[str, ...] = SOURCE_DIRS,
) -> list[str]:
    errors: list[str] = []
    for source_dir in source_dirs:
        root = project_root / source_dir
        if not root.exists():
            continue
        for py_file in root.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            for rule in rules:
                if rule.disallowed_import in content:
                    rel_path = py_file.relative_to(project_root)
                    errors.append(f"found typo import in {rel_path}")
    return errors


def run_known_typos_check(
    project_root: Path,
    rules: tuple[TypoRule, ...] | None = None,
    source_dirs: tuple[str, ...] = SOURCE_DIRS,
) -> list[str]:
    resolved_rules = rules or build_default_rules(project_root)
    return [
        *validate_target_packages(resolved_rules),
        *scan_typo_imports(project_root, resolved_rules, source_dirs),
    ]
