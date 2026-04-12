from abc import ABC
from abc import abstractmethod

from bs4 import BeautifulSoup

from scrapers.parsers.soup_parser_abc import HtmlSoupParserABC
from scrapers.section.parse_results import SectionParseResult


class SectionParserABC(HtmlSoupParserABC[SectionParseResult], ABC):
    """Canonical ABC for section parsers."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> SectionParseResult: ...


class NestedSectionParserABC(SectionParserABC, ABC):
    """Parser contract for nested section level."""


class SubSectionParserABC(NestedSectionParserABC, ABC):
    """Parser contract for subsection level."""


class SubSubSectionParserABC(SubSectionParserABC, ABC):
    """Parser contract for sub-subsection level."""
