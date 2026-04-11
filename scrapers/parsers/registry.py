from __future__ import annotations

from dataclasses import dataclass
from typing import Final
from typing import Literal

DomainName = Literal["drivers", "constructors", "circuits", "seasons", "grands_prix"]
ElementType = Literal["table", "list", "section", "infobox"]


@dataclass(frozen=True)
class ParserRegistryKey:
    domain: DomainName
    element_type: ElementType
    section_id: str | None = None


@dataclass(frozen=True)
class ParserRegistryEntry:
    key: ParserRegistryKey
    parser: str


DEFAULT_PARSER_REGISTRY: Final[tuple[ParserRegistryEntry, ...]] = (
    ParserRegistryEntry(
        key=ParserRegistryKey(domain="drivers", element_type="list"),
        parser="_parse_layer0_seed",
    ),
    ParserRegistryEntry(
        key=ParserRegistryKey(domain="drivers", element_type="section"),
        parser="_parse_layer1_details",
    ),
    ParserRegistryEntry(
        key=ParserRegistryKey(domain="constructors", element_type="list"),
        parser="_parse_layer0_seed",
    ),
    ParserRegistryEntry(
        key=ParserRegistryKey(domain="constructors", element_type="section"),
        parser="_parse_layer1_details",
    ),
    ParserRegistryEntry(
        key=ParserRegistryKey(domain="circuits", element_type="list"),
        parser="_parse_layer0_seed",
    ),
    ParserRegistryEntry(
        key=ParserRegistryKey(domain="circuits", element_type="section"),
        parser="_parse_layer1_details",
    ),
    ParserRegistryEntry(
        key=ParserRegistryKey(domain="seasons", element_type="list"),
        parser="_parse_layer0_seed",
    ),
    ParserRegistryEntry(
        key=ParserRegistryKey(domain="seasons", element_type="section"),
        parser="_parse_layer1_details",
    ),
    ParserRegistryEntry(
        key=ParserRegistryKey(domain="grands_prix", element_type="list"),
        parser="_parse_layer0_seed",
    ),
    ParserRegistryEntry(
        key=ParserRegistryKey(domain="grands_prix", element_type="section"),
        parser="_parse_layer1_details",
    ),
)


REQUIRED_PRODUCTION_KEYS: Final[tuple[ParserRegistryKey, ...]] = tuple(
    entry.key for entry in DEFAULT_PARSER_REGISTRY
)


def validate_parser_registry(
    registry: tuple[ParserRegistryEntry, ...] = DEFAULT_PARSER_REGISTRY,
    *,
    required_keys: tuple[ParserRegistryKey, ...] = REQUIRED_PRODUCTION_KEYS,
) -> None:
    duplicates: set[ParserRegistryKey] = set()
    seen: set[ParserRegistryKey] = set()

    for entry in registry:
        if entry.key in seen:
            duplicates.add(entry.key)
        seen.add(entry.key)

    if duplicates:
        details = ", ".join(
            sorted(
                f"{key.domain}:{key.element_type}:{key.section_id or '-'}"
                for key in duplicates
            )
        )
        raise ValueError(f"Parser registry conflict for keys: {details}")

    missing_keys = [key for key in required_keys if key not in seen]
    if missing_keys:
        details = ", ".join(
            f"{key.domain}:{key.element_type}:{key.section_id or '-'}"
            for key in missing_keys
        )
        raise ValueError(f"Missing parser registrations for keys: {details}")


def resolve_parser_name(
    *,
    domain: DomainName,
    element_type: ElementType,
    section_id: str | None = None,
    registry: tuple[ParserRegistryEntry, ...] = DEFAULT_PARSER_REGISTRY,
) -> str:
    key = ParserRegistryKey(
        domain=domain,
        element_type=element_type,
        section_id=section_id,
    )
    for entry in registry:
        if entry.key == key:
            return entry.parser
    raise LookupError(
        "No parser registration for "
        f"{domain}:{element_type}:{section_id or '-'}"
    )
