from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.data.parsed.figure import FigureParsedData
from models.data.parsed.infobox import InfoboxParsedData
from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.roles import HtmlTagParserABC
from scrapers.parsers.roles import MapperABC
from scrapers.parsers.roles import InfoboxHtmlParserABC
from scrapers.parsers.roles import ListHtmlParserABC
from scrapers.parsers.roles import ParserABC
from scrapers.parsers.roles import TableHtmlParserABC
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


class WikiSectionStructureParserABC(SectionElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup | Tag) -> WikiSectionParsedData: ...


class WikiInfoboxParserABC(InfoboxElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> InfoboxParsedData: ...


# Backward-compatible alias during migration.
WikiSectionStructureParserABC = WikiSectionParserABC


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
