from __future__ import annotations

from scrapers.parsers.wiki.domain_mapper import WikiDomainMapper
from scrapers.parsers.wiki.wiki_mapper_registry import WikiMapperRegistry


def build_default_domain_mapper() -> WikiDomainMapper:
    return WikiDomainMapper()


def build_default_mapper_registry() -> WikiMapperRegistry:
    return WikiMapperRegistry(domain_mapper=build_default_domain_mapper())


__all__ = [
    "build_default_domain_mapper",
    "build_default_mapper_registry",
]
