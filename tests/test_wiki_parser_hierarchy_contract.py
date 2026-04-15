from __future__ import annotations

from scrapers.parsers.parser_abc import ParserABC
from scrapers.parsers.registry import DEFAULT_PARSER_REGISTRY


def test_domain_parser_registry_uses_hierarchy_bases() -> None:
    for entry in DEFAULT_PARSER_REGISTRY:
        assert issubclass(
            entry.parser_base,
            ParserABC,
        ), f"{entry.parser_base} not a subclass of ParserABC"


def test_concrete_wiki_parsers_declare_expected_abc_and_parse_method() -> None:
    import ast
    from pathlib import Path

    expected = (
        (
            "scrapers/parsers/list_element_parser.py",
            "ListElementParser",
            "ParserABC",
        ),
        (
            "scrapers/parsers/wiki/element_references.py",
            "WikiReferencesElementParser",
            "ParserABC",
        ),
    )

    for file_path, parser_name, expected_base in expected:
        module = ast.parse(Path(file_path).read_text(encoding="utf-8"))
        parser_class = next(
            node
            for node in module.body
            if isinstance(node, ast.ClassDef) and node.name == parser_name
        )

        def _extract_base_name(base: ast.expr) -> str:
            text = ast.unparse(base)
            text = text.split("[", 1)[0]
            return text.split(".")[-1]

        base_names = [_extract_base_name(base) for base in parser_class.bases]
        assert expected_base in base_names
        assert any(
            isinstance(node, ast.FunctionDef) and node.name == "parse"
            for node in parser_class.body
        )
