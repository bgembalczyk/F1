from __future__ import annotations

import ast
from pathlib import Path

from scrapers.parsers.contracts.wiki_elements import WikiListElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiSectionElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiTableElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiInfoboxElementParserABC
from scrapers.parsers.registry import DEFAULT_PARSER_REGISTRY


def test_domain_parser_registry_uses_hierarchy_bases() -> None:
    _element_abcs = (
        WikiListElementParserABC,
        WikiSectionElementParserABC,
        WikiTableElementParserABC,
        WikiInfoboxElementParserABC,
    )
    for entry in DEFAULT_PARSER_REGISTRY:
        assert issubclass(entry.parser_base, _element_abcs), (
            f"{entry.parser_base} not a subclass of any element ABC"
        )


def test_concrete_wiki_parsers_declare_expected_abc_and_parse_method() -> None:
    expected = (
        ("scrapers/parsers/wiki/element_table.py", "WikiTableElementParser", "WikiTableElementParserABC"),
        ("scrapers/parsers/wiki/element_list.py", "WikiListElementParser", "WikiListElementParserABC"),
        (
            "scrapers/parsers/wiki/element_section.py",
            "WikiSectionElementParser",
            "WikiSectionElementParserABC",
        ),
        ("scrapers/parsers/wiki/element_infobox.py", "WikiInfoboxElementParser", "WikiInfoboxElementParserABC"),
    )

    for file_path, parser_name, expected_base in expected:
        module = ast.parse(Path(file_path).read_text(encoding="utf-8"))
        parser_class = next(
            node
            for node in module.body
            if isinstance(node, ast.ClassDef) and node.name == parser_name
        )
        base_names = [getattr(base, "id", getattr(base, "attr", "")) for base in parser_class.bases]
        assert expected_base in base_names
        assert any(
            isinstance(node, ast.FunctionDef) and node.name == "parse"
            for node in parser_class.body
        )
