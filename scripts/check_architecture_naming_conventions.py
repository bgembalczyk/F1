#!/usr/bin/env python3
"""Sanity-check dla konwencji nazewniczych modułów architektury."""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
PARSER_CANONICAL_PATH = Path("scrapers/parsers")
ALLOWED_PARSER_ABC_BASES = {
    "ParserABC",
    "SectionParserABC",
    "SectionStructureParserABC",
    "WikiSectionParserABC",
    "WikiSectionStructureParserABC",
    "WikiListParserABC",
    "WikiTableParserABC",
    "WikiFigureParserABC",
    "WikiInfoboxParserABC",
    "WikiNavboxParserABC",
    "TagParserABC",
    "TableParserABC",
    "TableElementParserABC",
    "SectionElementParserABC",
    "ElementParserABC",
    "HtmlTagParserABC",
    "HtmlElementParserABC",
    "SoupParserABC",
    "ArticleTablesParserABC",
    "FigureElementParserABC",
    "ListElementParserABC",
    "InfoboxElementParserABC",
    "InfoboxFieldParserABC",
    "ReferencesElementParserABC",
    "NavboxElementParserABC",
    "ParagraphElementParserABC",
}


def iter_python_files(paths: list[str]) -> list[Path]:
    if paths:
        candidates = [Path(path) for path in paths]
    else:
        candidates = [Path("scrapers"), Path("scripts")]

    files: list[Path] = []
    for candidate in candidates:
        if candidate.is_file() and candidate.suffix == ".py":
            files.append(candidate)
            continue
        if candidate.is_dir():
            files.extend(sorted(candidate.rglob("*.py")))
    return files


def validate_file_name(path: Path) -> list[str]:
    issues: list[str] = []
    name = path.name
    stem = path.stem

    if name == "__init__.py":
        return issues

    if not SNAKE_CASE_RE.fullmatch(stem):
        issues.append(f"{path}: plik nie jest snake_case")

    if stem == "base":
        issues.append(f"{path}: plik bazowy musi mieć nazwę *_base.py")

    return issues


def _is_mixin_context(path: Path) -> bool:
    if "mixins" in path.parts:
        return True
    return "mixin" in path.stem


def _is_public_parse_method(node: ast.stmt) -> bool:
    if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
        return False
    return node.name == "parse"


def _extract_base_name(base: ast.expr) -> str | None:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    if isinstance(base, ast.Subscript):
        return _extract_base_name(base.value)
    return None


def _inherits_allowed_parser_abc(node: ast.ClassDef) -> bool:
    base_names = {
        name
        for base in node.bases
        if (name := _extract_base_name(base))
    }
    return bool(
        base_names
        & {base for base in ALLOWED_PARSER_ABC_BASES if base.endswith("ABC")},
    )


def validate_class_names(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))

    issues: list[str] = []
    is_base_file = path.stem.endswith("_base")
    is_mixin_context = _is_mixin_context(path)

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        class_name = node.name

        if is_base_file and not class_name.endswith("Base"):
            issues.append(
                f"{path}:{node.lineno}: klasa w *_base.py musi kończyć się na 'Base'",
            )

        if is_mixin_context and not class_name.endswith("Mixin"):
            issues.append(
                f"{path}:{node.lineno}: klasa mixin musi kończyć się na 'Mixin'",
            )

        if not class_name.endswith("Parser"):
            continue

        if path.is_relative_to(PARSER_CANONICAL_PATH) and not _inherits_allowed_parser_abc(node):
            issues.append(
                f"{path}:{node.lineno}: klasa '*Parser' musi dziedziczyć po dozwolonym parser ABC",
            )

        has_public_parse = any(_is_public_parse_method(child) for child in node.body)
        if has_public_parse:
            continue
        issues.append(
            f"{path}:{node.lineno}: klasa '*Parser' bez parse(...) jest niedozwolona",
        )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Architecture naming conventions sanity-check.",
    )
    parser.add_argument("paths", nargs="*", help="Opcjonalne ścieżki do sprawdzenia")
    args = parser.parse_args()

    files = iter_python_files(args.paths)
    issues: list[str] = []

    for path in files:
        issues.extend(validate_file_name(path))
        issues.extend(validate_class_names(path))

    if issues:
        print("Wykryto odstępstwa od konwencji nazewniczych:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("OK: konwencje nazewnicze zachowane.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
