from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from bs4 import BeautifulSoup

from scrapers.parsers.contracts.wiki_elements import WikiSectionElementParserABC
from scrapers.section.parse_results import SectionParseResult


class SectionParserBase(WikiSectionElementParserABC, ABC):
    """Canonical implementation base for section parsers."""

    @abstractmethod
    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        """Parse a Wikipedia section fragment into the unified section DTO."""


__all__ = ["SectionParserBase"]
