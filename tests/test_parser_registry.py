from __future__ import annotations

import pytest

from scrapers.parsers.registry import ParsingRegistryEntry
from scrapers.parsers.registry import ParsingRegistryKey
from scrapers.parsers.registry import resolve_parser_base
from scrapers.parsers.registry import resolve_parser_name
from scrapers.parsers.registry import validate_parser_registry
from scrapers.parsers.element_parser_abc import ListElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiListParserABC


def test_validate_parser_registry_rejects_conflicts() -> None:
    duplicate_entries = (
        ParsingRegistryEntry(
            key=ParsingRegistryKey(domain="drivers", element_type="list"),
            parser_base=ListElementParserABC,
        ),
        ParsingRegistryEntry(
            key=ParsingRegistryKey(domain="drivers", element_type="list"),
            parser_base=ListElementParserABC,
        ),
    )

    with pytest.raises(ValueError, match="Parser registry conflict"):
        validate_parser_registry(
            duplicate_entries,
            required_keys=(ParsingRegistryKey(domain="drivers", element_type="list"),),
        )


def test_validate_parser_registry_rejects_missing_required_entries() -> None:
    partial_registry = (
        ParsingRegistryEntry(
            key=ParsingRegistryKey(domain="drivers", element_type="list"),
            parser_base=ListElementParserABC,
        ),
    )

    with pytest.raises(ValueError, match="Missing parser registrations"):
        validate_parser_registry(
            partial_registry,
            required_keys=(
                ParsingRegistryKey(domain="drivers", element_type="list"),
                ParsingRegistryKey(domain="drivers", element_type="section"),
            ),
        )


def test_resolve_parser_name_raises_for_unregistered_key() -> None:
    with pytest.raises(LookupError, match="No parser registration"):
        resolve_parser_name(domain="drivers", element_type="infobox", section_id="details")


def test_resolve_parser_base_returns_abc() -> None:
    parser_base = resolve_parser_base(domain="drivers", element_type="list")
    assert parser_base is WikiListParserABC
