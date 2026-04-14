from __future__ import annotations

import ast
from pathlib import Path

from tests.architecture.helpers import base_name

TARGET_FILES = (
    Path("scrapers/parsers/wiki/element_table.py"),
    Path("scrapers/parsers/list_element_parser.py"),
    Path("scrapers/parsers/wiki/element_section.py"),
    Path("scrapers/parsers/wiki/element_infobox.py"),
    Path("scrapers/parsers/wiki/element_navbox.py"),
    Path("scrapers/parsers/wiki/element_figure.py"),
)

ALLOWED_ROOTS = {
    "HtmlTagParserABC",
    "WikiInfoboxElementParserABC",
    "WikiFigureElementParserABC",
    "HtmlSoupParserABC",
}

ALLOWED_MIXINS = {
    "SafeParsingMixin",
}


def test_domain_wiki_element_parsers_use_element_abcs_and_optional_mixins() -> None:
    violations: list[str] = []

    for file_path in TARGET_FILES:
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or not node.name.endswith("Parser"):
                continue
            bases = tuple(base_name(base) for base in node.bases)
            if not any(base in ALLOWED_ROOTS for base in bases):
                violations.append(
                    f"{file_path}:{node.lineno} {node.name} musi dziedziczyć po Wiki*ParserABC/Wiki*ParserBase",
                )

            disallowed_mixins = [
                base
                for base in bases
                if base.endswith("Mixin") and base not in ALLOWED_MIXINS
            ]
            if disallowed_mixins:
                violations.append(
                    f"{file_path}:{node.lineno} {node.name} ma niedozwolone mixiny: {', '.join(disallowed_mixins)}",
                )

    assert not violations, "\n".join(violations)
