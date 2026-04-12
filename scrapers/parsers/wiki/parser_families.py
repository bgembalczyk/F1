from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.data.parsed.figure import FigureParsedData
from models.data.parsed.infobox import InfoboxParsedData
from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.roles import HtmlTagParserABC
from scrapers.parsers.roles import TableMapperABC
from scrapers.parsers.wiki.hierarchy import InfoboxElementParserABC
from scrapers.parsers.wiki.hierarchy import ListElementParserABC
from scrapers.parsers.wiki.hierarchy import SectionElementParserABC
from scrapers.parsers.wiki.hierarchy import TableElementParserABC

WikiTableParsedData = dict[str, Any]
WikiListParsedData = dict[str, Any]
WikiSectionParsedData = dict[str, Any]


class WikiTableParserABC(TableElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableParsedData: ...


class WikiListParserABC(ListElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListParsedData: ...


class WikiSectionParserABC(SectionElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup | Tag) -> WikiSectionParsedData: ...


class WikiSectionStructureParserABC(WikiSectionParserABC, ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup | Tag) -> WikiSectionParsedData: ...


class WikiInfoboxParserABC(InfoboxElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> InfoboxParsedData: ...


class WikiFigureHtmlParserABC(HtmlTagParserABC[FigureParsedData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> FigureParsedData: ...


class WikiNavboxHtmlParserABC(HtmlTagParserABC[NavBoxParsedData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> NavBoxParsedData: ...


@dataclass(frozen=True)
class WikiTableMapperSet:
    """Registry mapperów tabel (etap translacji parse -> domain)."""

    table_mapper: TableMapperABC | None = None


__all__ = [
    "WikiFigureHtmlParserABC",
    "WikiInfoboxParserABC",
    "WikiListParsedData",
    "WikiListParserABC",
    "WikiNavboxHtmlParserABC",
    "WikiSectionParsedData",
    "WikiSectionParserABC",
    "WikiSectionStructureParserABC",
    "WikiTableMapperSet",
    "WikiTableParsedData",
    "WikiTableParserABC",
]
