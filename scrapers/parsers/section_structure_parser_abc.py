from abc import ABC

from scrapers.parsers.wiki.section.base import BaseSectionParser


class SectionStructureParserABC(BaseSectionParser, ABC):
    """ABC for section parser hierarchy."""
