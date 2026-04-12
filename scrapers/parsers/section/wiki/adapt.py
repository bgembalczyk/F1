"""Compatibility re-export for section tree adapters."""

from scrapers.parsers.wiki.section_nodes.adapt import collect_section_elements
from scrapers.parsers.wiki.section_nodes.adapt import extract_sections
from scrapers.parsers.wiki.section_nodes.adapt import find_section_tree
from scrapers.parsers.wiki.section_nodes.adapt import iter_sections

__all__ = [
    "collect_section_elements",
    "extract_sections",
    "find_section_tree",
    "iter_sections",
]
