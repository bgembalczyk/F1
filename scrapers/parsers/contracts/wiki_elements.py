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
from scrapers.parsers.wiki.section_nodes.figure import WikiFigureParserABC as _WikiFigureParserABC
from scrapers.parsers.wiki.section_nodes.infobox import WikiInfoboxParserABC as _WikiInfoboxParserABC
from scrapers.parsers.wiki.section_nodes.list import WikiListParserABC as _WikiListParserABC
from scrapers.parsers.wiki.section_nodes.navbox import WikiNavboxParserABC as _WikiNavboxParserABC
from scrapers.parsers.wiki.section_nodes.section import WikiSectionParserABC as _WikiSectionParserABC
from scrapers.parsers.wiki.section_nodes.table import WikiTableParserABC as _WikiTableParserABC


class WikiTableParserABC(_WikiTableParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...


class WikiListParserABC(_WikiListParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...


class WikiSectionParserABC(_WikiSectionParserABC, ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> WikiSectionData: ...


class WikiInfoboxParserABC(_WikiInfoboxParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiInfoboxData: ...


class WikiNavboxParserABC(_WikiNavboxParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiNavboxData: ...


class WikiFigureParserABC(_WikiFigureParserABC, ABC):
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
