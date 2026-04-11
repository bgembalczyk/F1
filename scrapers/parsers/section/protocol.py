from __future__ import annotations

from scrapers.parsers.roles import SectionParserABC
from scrapers.parsers.section.base import BaseSectionParser
from scrapers.parsers.section.nested.nested_wiki import NestedWikiSectionParser


class SectionParser(NestedWikiSectionParser, BaseSectionParser, SectionParserABC):
    """Backward-compatible alias for the default nested wiki section parser."""


__all__ = ["BaseSectionParser", "SectionParserABC", "SectionParser"]
