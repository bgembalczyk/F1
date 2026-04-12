from __future__ import annotations

"""Backward-compatible parser ABC exports for section parsing.

Historically this module exposed protocol-like parser aliases.
New code should depend on concrete parser ABC classes from this module.
"""

from scrapers.parsers.roles import SectionParserABC
from scrapers.parsers.roles import SectionStructureParserABC
from scrapers.parsers.section.base import BaseSectionParser
from scrapers.parsers.wiki.nested_wiki import NestedWikiSectionParser

__all__ = [
    "BaseSectionParser",
    "NestedWikiSectionParser",
    "SectionParserABC",
    "SectionStructureParserABC",
]

# Backward-compatible alias. Prefer SectionParserABC in new code.
SectionParser = SectionParserABC
