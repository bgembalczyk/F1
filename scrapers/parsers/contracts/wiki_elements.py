from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from bs4 import BeautifulSoup
from bs4 import Tag

from models.data.wiki.figure import WikiFigureData
from models.data.wiki.infobox import WikiInfoboxData
from models.data.wiki.list import WikiListData
from models.data.wiki.navbox import WikiNavboxData
from models.data.wiki.section import WikiSectionData
from models.data.wiki.table import WikiTableData
from scrapers.parsers.element_parser_abc import FigureHtmlParserABC
from scrapers.parsers.element_parser_abc import ListHtmlParserABC
from scrapers.parsers.element_parser_abc import NavboxHtmlParserABC
from scrapers.parsers.element_parser_abc import SectionHtmlParserABC


class WikiListParserABC(ListHtmlParserABC[WikiListData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...


class WikiTableParserABC(WikiListParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...


class WikiSectionParserABC(SectionHtmlParserABC[WikiSectionData], ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> WikiSectionData: ...


class WikiInfoboxParserABC(WikiListParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiInfoboxData: ...


class WikiNavboxParserABC(NavboxHtmlParserABC[WikiNavboxData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiNavboxData: ...


class WikiFigureParserABC(FigureHtmlParserABC[WikiFigureData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiFigureData: ...


__all__ = [
    "WikiFigureParserABC",
    "WikiInfoboxParserABC",
    "WikiListParserABC",
    "WikiNavboxParserABC",
    "WikiSectionParserABC",
    "WikiTableParserABC",
]
