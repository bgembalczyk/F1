from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from bs4 import BeautifulSoup

from models.data.wiki.section import WikiSectionData
from scrapers.parsers.element_parser_abc import SectionHtmlParserABC


class WikiSectionParserABC(SectionHtmlParserABC[WikiSectionData], ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> WikiSectionData: ...


__all__ = ["WikiSectionParserABC"]
