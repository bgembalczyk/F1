from __future__ import annotations

import ast
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class FamilyRule:
    family: str
    required_bases: tuple[str, ...]


FAMILY_RULES = {
    "list": FamilyRule(
        family="list",
        required_bases=(
            "SeedListTableScraper",
            "F1ListScraper",
            "BaseConstructorListScraper",
        ),
    ),
    "table": FamilyRule(
        family="table",
        required_bases=(
            "F1TableScraper",
            "BaseEngineTableScraper",
            "SeedListTableScraper",
        ),
    ),
    "single_article": FamilyRule(
        family="single_article",
        required_bases=(
            "ArticleScraperBase",
            "SectionAdapterScraperBase",
            "SectionByIdScraperBase",
            "SectionAdapter",
        ),
    ),
    "section_parser": FamilyRule(
        family="section_parser",
        required_bases=("SectionParser", "BaseNestedSectionParser"),
    ),
}


def git_changed_python_files() -> list[Path]:
    merge_base_cmd = ["git", "merge-base", "origin/main", "HEAD"]
    merge_base = subprocess.run(
        merge_base_cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    diff_from = merge_base or "HEAD~1"
    cmd = [
        "git",
        "diff",
        "--name-only",
        "--diff-filter=AM",
        diff_from,
        "HEAD",
        "--",
        "*.py",
    ]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return [ROOT / file for file in files if file.startswith("scrapers/")]


def classify(class_name: str) -> str | None:
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


def base_names(class_def: ast.ClassDef) -> set[str]:
    names: set[str] = set()
    for base in class_def.bases:
        text = ast.unparse(base)
        names.add(text.split(".")[-1])
    return names


def validate_file(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    violations: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        family = classify(node.name)
        if family is None:
            continue

        rule = FAMILY_RULES[family]
        base_names = base_names(node)
        if not base_names.intersection(set(rule.required_bases)):
            violations.append(
                f"{path.relative_to(ROOT)}:{node.lineno} class {node.name} "
                f"must inherit one of {rule.required_bases} for family={rule.family}",
            )
    return violations


def main() -> int:
    changed_files = git_changed_python_files()
    violations: list[str] = []
    for file_path in changed_files:
        violations.extend(validate_file(file_path))

    if violations:
        print("::error::Scraper family contract violations detected:")
        for violation in violations:
            print(f"::error file={violation}")
        return 1

    print("Scraper family contracts check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
