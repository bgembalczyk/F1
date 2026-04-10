from __future__ import annotations

import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEGACY_FALLBACK_DEPRECATION_DATE = "2026-08-01"
ALLOWED_FAMILY_KINDS = {"list", "table", "single_article", "section_parser"}


@dataclass(frozen=True)
class FamilyRule:
    family: str
    root_classes: tuple[str, ...]
    required_contracts: tuple[str, ...]


FAMILY_RULES = {
    "list": FamilyRule(
        family="list",
        root_classes=(
            "SeedListTableScraper",
            "F1ListScraper",
            "BaseConstructorListScraper",
            "ListScraper",
        ),
        required_contracts=("ListScraperContract",),
    ),
    "table": FamilyRule(
        family="table",
        root_classes=("F1TableScraper", "BaseEngineTableScraper", "SeedListTableScraper"),
        required_contracts=("TableScraperContract",),
    ),
    "single_article": FamilyRule(
        family="single_article",
        root_classes=(
            "SingleWikiArticleScraperBase",
            "SingleArticleSectionAdapterBase",
            "SingleWikiArticleSectionAdapterBase",
            "SingleArticleSectionByIdBase",
            "SingleWikiArticleSectionByIdBase",
        ),
        required_contracts=("SingleArticleScraperContract",),
    ),
    "section_parser": FamilyRule(
        family="section_parser",
        root_classes=("SectionParser", "BaseNestedSectionParser"),
        required_contracts=("SectionParserContract",),
    ),
}


def _git_changed_python_files() -> list[Path]:
    merge_base_cmd = ["git", "merge-base", "origin/main", "HEAD"]
    merge_base = subprocess.run(
        merge_base_cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    diff_from = merge_base or "HEAD~1"
    cmd = ["git", "diff", "--name-only", "--diff-filter=AM", diff_from, "HEAD", "--", "*.py"]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return [ROOT / file for file in files if file.startswith("scrapers/")]


def _classify_by_name(class_name: str) -> str | None:
    if class_name.endswith("SectionParser"):
        return "section_parser"
    if not class_name.endswith("Scraper"):
        return None
    if "Single" in class_name:
        return "single_article"
    if "List" in class_name:
        return "list"
    if "Table" in class_name:
        return "table"
    return None


def _base_names(class_def: ast.ClassDef) -> set[str]:
    names: set[str] = set()
    for base in class_def.bases:
        text = ast.unparse(base)
        names.add(text.split(".")[-1])
    return names


def _literal_str_attr(class_def: ast.ClassDef, attr_name: str) -> str | None:
    for stmt in class_def.body:
        if not isinstance(stmt, ast.Assign):
            continue
        if len(stmt.targets) != 1:
            continue
        target = stmt.targets[0]
        if isinstance(target, ast.Name) and target.id == attr_name:
            value = stmt.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                return value.value
    return None


def _is_legacy_class(path: Path, class_name: str) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return "/legacy/" in rel or class_name.startswith("Legacy")


def _validate_file(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    violations: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        declared_family = _literal_str_attr(node, "FAMILY_KIND")
        family = declared_family
        if family is None and _is_legacy_class(path, node.name):
            family = _classify_by_name(node.name)
        if family is None:
            continue
        if family not in ALLOWED_FAMILY_KINDS:
            violations.append(
                f"{path.relative_to(ROOT)}:{node.lineno} class {node.name} "
                f"defines unsupported FAMILY_KIND={family!r}; allowed={sorted(ALLOWED_FAMILY_KINDS)}",
            )
            continue
        rule = FAMILY_RULES[family]
        base_names = _base_names(node)
        is_root_class = node.name in rule.root_classes
        required_bases = set(rule.required_contracts if is_root_class else rule.root_classes)
        if not base_names.intersection(required_bases):
            violations.append(
                f"{path.relative_to(ROOT)}:{node.lineno} class {node.name} "
                f"must inherit one of {tuple(required_bases)} for family={rule.family}",
            )
    return violations


def _legacy_fallback_usages(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    fallbacks: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        declared_family = _literal_str_attr(node, "FAMILY_KIND")
        if declared_family is None and _is_legacy_class(path, node.name):
            guessed = _classify_by_name(node.name)
            if guessed is not None:
                fallbacks.append(
                    f"{path.relative_to(ROOT)}:{node.lineno} class {node.name} "
                    f"(guessed family={guessed})",
                )
    return fallbacks


def main() -> int:
    changed_files = _git_changed_python_files()
    violations: list[str] = []
    legacy_fallbacks: list[str] = []
    for file_path in changed_files:
        violations.extend(_validate_file(file_path))
        legacy_fallbacks.extend(_legacy_fallback_usages(file_path))

    if violations:
        print("::error::Scraper family contract violations detected:")
        for violation in violations:
            print(f"::error file={violation}")
        return 1

    if legacy_fallbacks:
        print("::warning::Legacy naming fallback is in use.")
        print(
            f"::warning::Fallback classification will be disabled after "
            f"{LEGACY_FALLBACK_DEPRECATION_DATE}.",
        )
        for fallback in legacy_fallbacks:
            print(f"::warning file={fallback}")

    print("Scraper family contracts check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
