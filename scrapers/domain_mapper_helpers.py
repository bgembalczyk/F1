from __future__ import annotations

from scrapers.identity_domain_mapper import IdentityDomainMapper
from scrapers.domain_mapper_abc import DomainMapperABC
from scrapers.parsers.wiki.wiki_mapper_registry import WikiMapperRegistry


def build_default_domain_mapper() -> DomainMapperABC:
    return IdentityDomainMapper()


def build_default_mapper_registry() -> WikiMapperRegistry:
    return WikiMapperRegistry(domain_mapper=build_default_domain_mapper())


__all__ = [
    "build_default_domain_mapper",
    "build_default_mapper_registry",
]
