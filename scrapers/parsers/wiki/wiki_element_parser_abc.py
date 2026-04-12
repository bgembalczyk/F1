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
from scrapers.parsers.element_parser_abc import InfoboxHtmlParserABC
from scrapers.parsers.element_parser_abc import ListHtmlParserABC
from scrapers.parsers.element_parser_abc import NavboxHtmlParserABC
from scrapers.parsers.element_parser_abc import SectionHtmlParserABC
from scrapers.parsers.element_parser_abc import TableHtmlParserABC


class WikiTableElementParserABC(TableHtmlParserABC[WikiTableData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...


class WikiListElementParserABC(ListHtmlParserABC[WikiListData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...


class WikiSectionElementParserABC(SectionHtmlParserABC[WikiSectionData], ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> WikiSectionData: ...


class WikiInfoboxElementParserABC(InfoboxHtmlParserABC[WikiInfoboxData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiInfoboxData: ...


class WikiNavboxElementParserABC(NavboxHtmlParserABC[WikiNavboxData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiNavboxData: ...


class WikiFigureElementParserABC(FigureHtmlParserABC[WikiFigureData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiFigureData: ...


# Backward-compatible aliases for legacy imports.
WikiTableParserABC = WikiTableElementParserABC
WikiListParserABC = WikiListElementParserABC
WikiSectionParserABC = WikiSectionElementParserABC
WikiInfoboxParserABC = WikiInfoboxElementParserABC
WikiNavboxParserABC = WikiNavboxElementParserABC
WikiFigureParserABC = WikiFigureElementParserABC


__all__ = [
    "WikiFigureElementParserABC",
    "WikiFigureParserABC",
    "WikiInfoboxElementParserABC",
    "WikiInfoboxParserABC",
    "WikiListElementParserABC",
    "WikiListParserABC",
    "WikiNavboxElementParserABC",
    "WikiNavboxParserABC",
    "WikiSectionElementParserABC",
    "WikiSectionParserABC",
    "WikiTableElementParserABC",
    "WikiTableParserABC",
]
