from __future__ import annotations

import ast
from pathlib import Path

from scrapers.parsers.wiki.wiki_list_parser_abc import WikiListParserABC
from scrapers.parsers.wiki.wiki_section_parser_abc import WikiSectionParserABC
from scrapers.parsers.registry import DEFAULT_PARSER_REGISTRY


def test_domain_parser_registry_uses_hierarchy_bases() -> None:
    for entry in DEFAULT_PARSER_REGISTRY:
        assert issubclass(
            entry.parser_base,
            (WikiListParserABC, WikiSectionParserABC),
        )


def test_concrete_wiki_parsers_declare_expected_abc_and_parse_method() -> None:
    expected = (
        ("scrapers/parsers/wiki/element_table.py", "WikiTableElementParser", "WikiTableParserABC"),
        ("scrapers/parsers/wiki/element_list.py", "WikiListElementParser", "WikiListParserABC"),
        (
            "scrapers/parsers/wiki/element_section.py",
            "WikiSectionElementParser",
            "WikiSectionStructureParserABC",
        ),
        ("scrapers/parsers/wiki/element_infobox.py", "WikiInfoboxElementParser", "WikiInfoboxParserABC"),
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
