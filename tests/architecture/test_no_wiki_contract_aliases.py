from __future__ import annotations

import ast
from pathlib import Path

from tests.architecture.helpers import python_files

REMOVED_MODULES = (
    "scrapers.parsers.wiki.hierarchy",
    "scrapers.parsers.wiki.parser_families",
)

REMOVED_FILES = (
    Path("scrapers/parsers/wiki/section_nodes/list.py"),
    Path("scrapers/parsers/wiki/section_nodes/table.py"),
    Path("scrapers/parsers/wiki/section_nodes/infobox.py"),
    Path("scrapers/parsers/wiki/section_nodes/section.py"),
    Path("scrapers/parsers/wiki/section_nodes/navbox.py"),
    Path("scrapers/parsers/wiki/section_nodes/figure.py"),
)

REMOVED_SYMBOLS_BY_MODULE = {
    "scrapers.parsers.contracts.wiki_elements": {
        "WikiFigureHtmlParserABC",
        "WikiInfoboxSectionParserABC",
        "WikiListSectionParserABC",
        "WikiNavboxHtmlParserABC",
        "WikiTableSectionParserABC",
    },
}


def test_removed_wiki_contract_alias_modules_stay_deleted() -> None:
    for module_path in (
        Path("scrapers/parsers/wiki/hierarchy.py"),
        Path("scrapers/parsers/wiki/parser_families.py"),
        *REMOVED_FILES,
    ):
        assert not module_path.exists(), f"Alias module restored: {module_path}"


def test_no_imports_from_removed_wiki_contract_alias_modules() -> None:
    violations: list[str] = []
    for path in python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in REMOVED_MODULES:
                        violations.append(f"{path}:{node.lineno}:{alias.name}")
            if isinstance(node, ast.ImportFrom) and node.module in REMOVED_MODULES:
                violations.append(f"{path}:{node.lineno}:{node.module}")
    assert not violations, "Forbidden imports from removed alias modules: " + ", ".join(
        violations,
    )


def test_no_imports_of_removed_wiki_contract_alias_symbols() -> None:
    violations: list[str] = []
    for path in python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if not node.module or node.module not in REMOVED_SYMBOLS_BY_MODULE:
                continue
            removed_symbols = REMOVED_SYMBOLS_BY_MODULE[node.module]
            for alias in node.names:
                if alias.name in removed_symbols:
                    violations.append(
                        f"{path}:{node.lineno}:{node.module}.{alias.name}",
                    )
    assert not violations, "Forbidden imports of removed alias symbols: " + ", ".join(
        violations,
    )
