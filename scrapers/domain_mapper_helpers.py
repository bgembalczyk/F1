"""Compatibility shim for mapper helper imports."""

from scrapers.mappers.domain_mapper_helpers import build_default_domain_mapper
from scrapers.mappers.domain_mapper_helpers import build_default_mapper_registry
from scrapers.parsers.wiki.wiki_mapper_registry import WikiMapperRegistry

__all__ = [
    "WikiMapperRegistry",
    "build_default_domain_mapper",
    "build_default_mapper_registry",
]
