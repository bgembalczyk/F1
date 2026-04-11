from __future__ import annotations

import pytest

from scrapers.parsers.registry import ParserRegistryEntry
from scrapers.parsers.registry import ParserRegistryKey
from scrapers.parsers.registry import resolve_parser_name
from scrapers.parsers.registry import validate_parser_registry


def test_validate_parser_registry_rejects_conflicts() -> None:
    duplicate_entries = (
        ParserRegistryEntry(
            key=ParserRegistryKey(domain="drivers", element_type="list"),
            parser="drivers.list.parser.a",
        ),
        ParserRegistryEntry(
            key=ParserRegistryKey(domain="drivers", element_type="list"),
            parser="drivers.list.parser.b",
        ),
    )

    with pytest.raises(ValueError, match="Parser registry conflict"):
        validate_parser_registry(
            duplicate_entries,
            required_keys=(ParserRegistryKey(domain="drivers", element_type="list"),),
        )


def test_validate_parser_registry_rejects_missing_required_entries() -> None:
    partial_registry = (
        ParserRegistryEntry(
            key=ParserRegistryKey(domain="drivers", element_type="list"),
            parser="drivers.list.parser",
        ),
    )

    with pytest.raises(ValueError, match="Missing parser registrations"):
        validate_parser_registry(
            partial_registry,
            required_keys=(
                ParserRegistryKey(domain="drivers", element_type="list"),
                ParserRegistryKey(domain="drivers", element_type="section"),
            ),
        )


def test_resolve_parser_name_raises_for_unregistered_key() -> None:
    with pytest.raises(LookupError, match="No parser registration"):
        resolve_parser_name(domain="drivers", element_type="infobox")
