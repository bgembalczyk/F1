from __future__ import annotations

from scrapers.wiki.parsers.sections.adapter import collect_section_elements
from scrapers.wiki.parsers.sections.adapter import find_section_tree
from scrapers.wiki.parsers.sections.data_classes import SectionExtractionContext

__all__ = [
    "SectionExtractionContext",
    "collect_section_elements",
    "find_section_tree",
]
