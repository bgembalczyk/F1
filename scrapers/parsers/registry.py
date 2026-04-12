from __future__ import annotations

import importlib
import inspect
import pkgutil
from dataclasses import dataclass
from typing import Final
from typing import Literal
from typing import TypeAlias

import scrapers.parsers as parsers_pkg
from scrapers.parsers.parser_abc import ParserABC
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiInfoboxElementParserABC
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiListElementParserABC
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiSectionElementParserABC
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiTableElementParserABC

DomainName = Literal["drivers", "constructors", "circuits", "seasons", "grands_prix"]
ElementType = Literal["table", "list", "section", "infobox"]
ParserBase: TypeAlias = type[ParserABC[object, object]]


@dataclass(frozen=True)
class ParsingRegistryKey:
    domain: DomainName
    element_type: ElementType
    section_id: str | None = None


@dataclass(frozen=True)
class ParsingRegistryEntry:
    key: ParsingRegistryKey
    parser_base: ParserBase


AUTO_ELEMENT_PARSER_BASES: Final[dict[ElementType, ParserBase]] = {
    "table": WikiTableElementParserABC,
    "list": WikiListElementParserABC,
    "section": WikiSectionElementParserABC,
    "infobox": WikiInfoboxElementParserABC,
}

DEFAULT_PARSER_REGISTRY: Final[tuple[ParsingRegistryEntry, ...]] = tuple(
    ParsingRegistryEntry(
        key=ParsingRegistryKey(domain=domain, element_type=element_type),
        parser_base=parser_base,
    )
    for domain in ("drivers", "constructors", "circuits", "seasons", "grands_prix")
    for element_type, parser_base in AUTO_ELEMENT_PARSER_BASES.items()
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


def discover_registered_parser_classes() -> tuple[type[ParserABC[object, object]], ...]:
    """Discover concrete parser classes in scrapers.parsers package.

    Rule: class name ending with `Parser` must implement parser contract
    (inherit from ParserABC) to be considered a registered parser class.
    """
    discovered: list[type[ParserABC[object, object]]] = []
    for module_info in pkgutil.walk_packages(
        parsers_pkg.__path__,
        prefix=f"{parsers_pkg.__name__}.",
    ):
        try:
            module = importlib.import_module(module_info.name)
        except Exception:
            continue
        for _, class_type in inspect.getmembers(module, inspect.isclass):
            if class_type.__module__ != module.__name__:
                continue
            if not class_type.__name__.endswith("Parser"):
                continue
            if inspect.isabstract(class_type):
                continue
            if not issubclass(class_type, ParserABC):
                continue
            discovered.append(class_type)
    return tuple(sorted(discovered, key=lambda cls: f"{cls.__module__}.{cls.__name__}"))


def is_parser_class_registered(class_type: type[object]) -> bool:
    """Return True when class is detected by parser class registry discovery."""
    if not inspect.isclass(class_type):
        return False
    return class_type in set(discover_registered_parser_classes())


__all__ = [
    "DEFAULT_PARSER_REGISTRY",
    "DomainName",
    "ElementType",
    "ParsingRegistryEntry",
    "ParsingRegistryKey",
    "REQUIRED_PRODUCTION_KEYS",
    "discover_registered_parser_classes",
    "is_parser_class_registered",
    "resolve_parser_base",
    "resolve_parser_name",
    "validate_parser_registry",
]
