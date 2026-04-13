from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from bs4 import BeautifulSoup

from scrapers.parsers.element_parser_abc import HtmlSoupParserABC
from scrapers.section.parse_results import SectionParseResult


class SectionParserBase(HtmlSoupParserABC[SectionParseResult], ABC):
    """Canonical implementation base for section parsers."""

    @abstractmethod
    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        """Parse a Wikipedia section fragment into the unified section DTO."""

    def _parse_group(self, *args: object, **kwargs: object) -> object:
        """Wewnętrzny helper dla parserów opartych o grupowanie elementów."""

        _ = args
        _ = kwargs
        raise NotImplementedError

    def _parse_children(self, *args: object, **kwargs: object) -> object:
        """Wewnętrzny helper dla parserów opartych o iterację po dzieciach."""

        _ = args
        _ = kwargs
        raise NotImplementedError


__all__ = ["SectionParserBase"]
