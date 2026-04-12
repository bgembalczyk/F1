"""Compatibility re-export for section profile helpers."""

from scrapers.parsers.wiki.section_nodes.helpers import DOMAIN_SECTION_PROFILES
from scrapers.parsers.wiki.section_nodes.helpers import profile_entry_aliases
from scrapers.parsers.wiki.section_nodes.helpers import split_into_parts

__all__ = [
    "DOMAIN_SECTION_PROFILES",
    "profile_entry_aliases",
    "split_into_parts",
]
