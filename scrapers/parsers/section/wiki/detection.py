"""Compatibility re-export for section heading detection."""

from scrapers.parsers.wiki.section_nodes.detection import find_section_heading
from scrapers.parsers.wiki.section_nodes.detection import make_stable_section_id
from scrapers.parsers.wiki.section_nodes.detection import normalize_section_slug

__all__ = [
    "find_section_heading",
    "make_stable_section_id",
    "normalize_section_slug",
]
