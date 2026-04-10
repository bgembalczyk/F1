from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

SUGGESTIVE_TOKENS = ("COMPLETE", "FULL")
MIN_DOMAIN_REQUIRED_FIELDS = 3
NON_DOMAIN_FIELDS = {"url", "id", "source_url", "href", "link"}


@dataclass(frozen=True)
class SchemaSemanticsIssue:
    path: Path
    line: int
    schema_name: str
    required_fields: tuple[str, ...]

    def format(self) -> str:
        return (
            f"{self.path}:{self.line}: schema '{self.schema_name}' sugeruje pełność "
            f"(complete/full), ale ma zbyt mało wymaganych pól domenowych: "
            f"{self.required_fields}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Wymusza, aby schemy sugerujące complete/full miały minimalny "
            "zestaw wymaganych pól domenowych."
        ),
    )
    parser.add_argument(
        "--root",
        default="models/records",
        help="Root directory with record schemas.",
    )
    return parser.parse_args()


def _has_complete_or_full_token(name: str) -> bool:
    upper = name.upper()
    return any(token in upper for token in SUGGESTIVE_TOKENS)


def _extract_required_tuple(call: ast.Call) -> tuple[str, ...]:
    for keyword in call.keywords:
        if keyword.arg != "required":
            continue
        value = keyword.value
        if isinstance(value, (ast.Tuple, ast.List)):
            fields: list[str] = []
            for element in value.elts:
                if isinstance(element, ast.Constant) and isinstance(element.value, str):
                    fields.append(element.value)
            return tuple(fields)
    return ()


def _is_schema_constructor(call: ast.Call) -> bool:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id in {"RecordSchema", "RecordDefinition"}
    if isinstance(func, ast.Attribute):
        return func.attr in {"RecordSchema", "RecordDefinition"}
    return False


def _collect_issues_for_file(path: Path) -> list[SchemaSemanticsIssue]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    issues: list[SchemaSemanticsIssue] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        schema_name = node.targets[0].id
        if not _has_complete_or_full_token(schema_name):
            continue
        if not isinstance(node.value, ast.Call) or not _is_schema_constructor(node.value):
            continue

        required_fields = _extract_required_tuple(node.value)
        domain_required = tuple(
            field for field in required_fields if field not in NON_DOMAIN_FIELDS
        )
        if len(domain_required) >= MIN_DOMAIN_REQUIRED_FIELDS:
            continue

        issues.append(
            SchemaSemanticsIssue(
                path=path,
                line=node.lineno,
                schema_name=schema_name,
                required_fields=required_fields,
            ),
        )

    return issues


def run(root: Path) -> list[str]:
    all_issues: list[str] = []
    for file_path in sorted(root.rglob("*.py")):
        all_issues.extend(issue.format() for issue in _collect_issues_for_file(file_path))
    return all_issues


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    issues = run(root)
    if issues:
        for issue in issues:
            print(f"::error::{issue}")
        return 1

    print("[complete-schema-semantics] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
