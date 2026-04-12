"""Canonical section-heading detection utilities."""

from scrapers.parsers.section.detection import find_section_heading
from scrapers.parsers.section.detection import make_stable_section_id
from scrapers.parsers.section.detection import normalize_section_slug

__all__ = [
    "find_section_heading",
    "make_stable_section_id",
    "normalize_section_slug",
]
