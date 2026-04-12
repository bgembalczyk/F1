from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scrapers.parsers.wiki.families import WikiTableMapperSet


class DomainMapperABC:
    """Mapuje parsed payload wiki na rekordy domenowe."""

    def map(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


@dataclass(frozen=True)
class IdentityDomainMapper(DomainMapperABC):
    """Domyślny mapper: brak mapowania."""

    def map(self, payload: dict[str, Any]) -> dict[str, Any]:
        return payload


@dataclass(frozen=True)
class WikiMapperRegistry:
    """Jawny registry mapperów używanych wyłącznie w etapie translacji domenowej."""

    domain_mapper: DomainMapperABC
    table_mappers: WikiTableMapperSet = WikiTableMapperSet()


def build_default_domain_mapper() -> DomainMapperABC:
    return IdentityDomainMapper()


def build_default_mapper_registry() -> WikiMapperRegistry:
    return WikiMapperRegistry(domain_mapper=build_default_domain_mapper())


__all__ = [
    "DomainMapperABC",
    "IdentityDomainMapper",
    "WikiMapperRegistry",
    "build_default_domain_mapper",
    "build_default_mapper_registry",
]
