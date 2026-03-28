from __future__ import annotations

from scrapers.wiki.parsers.sections.detection import find_section_heading
from scrapers.wiki.parsers.sections.detection import make_stable_section_id
from scrapers.wiki.parsers.sections.detection import normalize_section_slug

__all__ = [
    "find_section_heading",
    "make_stable_section_id",
    "normalize_section_slug",
]
