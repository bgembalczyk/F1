# ruff: noqa: E501
from __future__ import annotations

import ast
from dataclasses import asdict
from pathlib import Path

from bs4 import BeautifulSoup

from scrapers.parsers.section.circuit.layout_history import (
    CircuitLayoutHistorySectionParser,
)
from scrapers.parsers.section.table.constructor.history import (
    ConstructorHistorySectionParser,
)
from scrapers.parsers.section.grand_prix.by_year import (
    GrandPrixByYearSectionParser,
)
from scrapers.parsers.section.changes.season import SeasonRegulationChangesSectionParser

CONTRACT_KEYS = ("section_id", "section_label", "records", "metadata")
PARSER_CONTRACT_SCOPES = (
    Path("scrapers/parsers/section"),
    Path("scrapers/parsers/wiki/base_nested_section"),
)
PARSER_ABSTRACT_BASE_NAMES = {
    "BaseSectionParser",
    "BaseNestedSectionParser",
    "TableSectionParser",
    "ConstructorTablesSectionParser",
    "ConstructorsSectionParser",
    "NestedWikiSectionParser",
    "SubSectionParser",
    "SubSubSectionParser",
    "WikiTableHtmlParser",
}


def _base_name(base: ast.expr) -> str:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    if isinstance(base, ast.Subscript):
        return _base_name(base.value)
    return ast.unparse(base)


def test_constructor_section_parser_contract() -> None:
    parser = ConstructorHistorySectionParser()
    result = parser.parse(
        BeautifulSoup(
            '<table class="wikitable"><tr><th>Year</th></tr><tr><td>1950</td></tr></table>',
            "html.parser",
        ),
    )
    assert tuple(asdict(result).keys()) == CONTRACT_KEYS


def test_circuit_section_parser_contract() -> None:
    parser = CircuitLayoutHistorySectionParser()
    result = parser.parse(BeautifulSoup("<p>First layout</p>", "html.parser"))
    assert tuple(asdict(result).keys()) == CONTRACT_KEYS


def test_season_section_parser_contract() -> None:
    parser = SeasonRegulationChangesSectionParser()
    result = parser.parse(
        BeautifulSoup("<ul><li>Rules update</li></ul>", "html.parser"),
    )
    assert tuple(asdict(result).keys()) == CONTRACT_KEYS


def test_grand_prix_section_parser_contract() -> None:
    parser = GrandPrixByYearSectionParser(
        url="https://example.com/gp",
        include_urls=False,
        normalize_empty_values=True,
    )
    html = """<table class="wikitable">
      <tr><th>Year</th><th>Driver</th><th>Constructor</th><th>Report</th></tr>
      <tr><td>2024</td><td>Max Verstappen</td><td>Red Bull-Ford</td><td>Race report</td></tr>
    </table>"""
    result = parser.parse(BeautifulSoup(html, "html.parser"))
    assert tuple(asdict(result).keys()) == CONTRACT_KEYS


def test_section_parsers_define_explicit_parse_or_are_abstract() -> None:
    violations: list[str] = []
    for scope in PARSER_CONTRACT_SCOPES:
        for path in sorted(scope.rglob("*.py")):
            module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in module.body:
                if not isinstance(node, ast.ClassDef) or not node.name.endswith("Parser"):
                    continue
                base_names = {_base_name(base) for base in node.bases}
                has_parse = any(
                    isinstance(item, ast.FunctionDef) and item.name == "parse"
                    for item in node.body
                )
                inherits_parser_abc = any(
                    base_name.endswith("ParserABC") for base_name in base_names
                ) or bool(base_names & PARSER_ABSTRACT_BASE_NAMES)
                is_abc = "ABC" in base_names
                if not inherits_parser_abc:
                    violations.append(
                        f"{path}:{node.name} does not inherit *ParserABC",
                    )
                    continue
                if not has_parse and not is_abc:
                    violations.append(
                        f"{path}:{node.name} has no parse() and is not ABC",
                    )
    assert not violations, "Section parser contract violations: " + ", ".join(violations)
