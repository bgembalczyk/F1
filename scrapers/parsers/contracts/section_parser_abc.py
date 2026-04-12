from abc import ABC
from abc import abstractmethod

from bs4 import BeautifulSoup

from scrapers.parsers.contracts.base import ParserABC
from scrapers.section.parse_results import SectionParseResult


class SectionParserABC(ParserABC[BeautifulSoup, SectionParseResult], ABC):
    """Canonical ABC for section parsers."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> SectionParseResult: ...

