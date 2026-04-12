from __future__ import annotations

from dataclasses import dataclass
from typing import Final
from typing import Literal
from typing import TypeAlias

from scrapers.parsers.wiki.hierarchy import ElementParserABC
from scrapers.parsers.wiki.hierarchy import ListElementParserABC
from scrapers.parsers.wiki.hierarchy import SectionElementParserABC

DomainName = Literal["drivers", "constructors", "circuits", "seasons", "grands_prix"]
ElementType = Literal["table", "list", "section", "infobox"]
ParserBase: TypeAlias = type[ElementParserABC]


@dataclass(frozen=True)
class ParsingRegistryKey:
    domain: DomainName
    element_type: ElementType
    section_id: str | None = None


@dataclass(frozen=True)
class ParsingRegistryEntry:
    key: ParsingRegistryKey
    parser_base: ParserBase


DEFAULT_PARSER_REGISTRY: Final[tuple[ParsingRegistryEntry, ...]] = (
    ParsingRegistryEntry(
        key=ParsingRegistryKey(domain="drivers", element_type="list"),
        parser_base=ListElementParserABC,
    ),
    ParsingRegistryEntry(
        key=ParsingRegistryKey(domain="drivers", element_type="section"),
        parser_base=SectionElementParserABC,
    ),
    ParsingRegistryEntry(
        key=ParsingRegistryKey(domain="constructors", element_type="list"),
        parser_base=ListElementParserABC,
    ),
    ParsingRegistryEntry(
        key=ParsingRegistryKey(domain="constructors", element_type="section"),
        parser_base=SectionElementParserABC,
    ),
    ParsingRegistryEntry(
        key=ParsingRegistryKey(domain="circuits", element_type="list"),
        parser_base=ListElementParserABC,
    ),
    ParsingRegistryEntry(
        key=ParsingRegistryKey(domain="circuits", element_type="section"),
        parser_base=SectionElementParserABC,
    ),
    ParsingRegistryEntry(
        key=ParsingRegistryKey(domain="seasons", element_type="list"),
        parser_base=ListElementParserABC,
    ),
    ParsingRegistryEntry(
        key=ParsingRegistryKey(domain="seasons", element_type="section"),
        parser_base=SectionElementParserABC,
    ),
    ParsingRegistryEntry(
        key=ParsingRegistryKey(domain="grands_prix", element_type="list"),
        parser_base=ListElementParserABC,
    ),
    ParsingRegistryEntry(
        key=ParsingRegistryKey(domain="grands_prix", element_type="section"),
        parser_base=SectionElementParserABC,
    ),
)


REQUIRED_PRODUCTION_KEYS: Final[tuple[ParsingRegistryKey, ...]] = tuple(
    entry.key for entry in DEFAULT_PARSER_REGISTRY
)


def validate_parser_registry(
    registry: tuple[ParsingRegistryEntry, ...] = DEFAULT_PARSER_REGISTRY,
    *,
    required_keys: tuple[ParsingRegistryKey, ...] = REQUIRED_PRODUCTION_KEYS,
) -> None:
    duplicates: set[ParsingRegistryKey] = set()
    seen: set[ParsingRegistryKey] = set()

    for entry in registry:
        if entry.key in seen:
            duplicates.add(entry.key)
        seen.add(entry.key)

    if duplicates:
        details = ", ".join(
            sorted(
                f"{key.domain}:{key.element_type}:{key.section_id or '-'}"
                for key in duplicates
            ),
        )
        raise ValueError(f"Parser registry conflict for keys: {details}")

    missing_keys = [key for key in required_keys if key not in seen]
    if missing_keys:
        details = ", ".join(
            f"{key.domain}:{key.element_type}:{key.section_id or '-'}"
            for key in missing_keys
        )
        raise ValueError(f"Missing parser registrations for keys: {details}")


def resolve_parser_base(
    *,
    domain: DomainName,
    element_type: ElementType,
    section_id: str | None = None,
    registry: tuple[ParsingRegistryEntry, ...] = DEFAULT_PARSER_REGISTRY,
) -> ParserBase:
    key = ParsingRegistryKey(
        domain=domain,
        element_type=element_type,
        section_id=section_id,
    )
    for entry in registry:
        if entry.key == key:
            return entry.parser_base
    raise LookupError(
        "No parser registration for " f"{domain}:{element_type}:{section_id or '-'}",
    )


def resolve_parser_name(
    *,
    domain: DomainName,
    element_type: ElementType,
    section_id: str | None = None,
    registry: tuple[ParsingRegistryEntry, ...] = DEFAULT_PARSER_REGISTRY,
) -> str:
    return resolve_parser_base(
        domain=domain,
        element_type=element_type,
        section_id=section_id,
        registry=registry,
    ).__name__


__all__ = [
    "DEFAULT_PARSER_REGISTRY",
    "DomainName",
    "ElementType",
    "ParsingRegistryEntry",
    "ParsingRegistryKey",
    "REQUIRED_PRODUCTION_KEYS",
    "resolve_parser_base",
    "resolve_parser_name",
    "validate_parser_registry",
]
