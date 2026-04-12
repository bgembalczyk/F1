from __future__ import annotations

from scrapers.parsers.roles import SectionStructureParserABC
from scrapers.parsers.section.base import BaseSectionParser
from scrapers.parsers.wiki.nested_wiki import NestedWikiSectionParser

__all__ = [
    "BaseSectionParser",
    "NestedWikiSectionParser",
    "SectionStructureParserABC",
]
