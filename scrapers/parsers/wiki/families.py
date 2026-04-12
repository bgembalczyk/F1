from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.data.parsed.figure import FigureParsedData
from models.data.parsed.html_elements import SectionElementData
from models.data.parsed.infobox import InfoboxParsedData
from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.base_family import InfoboxParserABC
from scrapers.parsers.base_family import ListParserABC
from scrapers.parsers.base_family import SectionParserABC
from scrapers.parsers.base_family import TableParserABC
from scrapers.parsers.base_family import TagParserABC
from scrapers.parsers.roles import TableMapperABC

WikiTableParsedData = dict[str, Any]
WikiListParsedData = dict[str, Any]
WikiSectionParsedData = SectionElementData


class WikiTableParserABC(TagParserABC[WikiTableParsedData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableParsedData: ...


class WikiListParserABC(ListParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListParsedData: ...


class WikiSectionParserABC(SectionElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> WikiSectionParsedData: ...


class WikiSectionStructureParserABC(WikiSectionParserABC, ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup | Tag) -> WikiSectionParsedData: ...


class WikiInfoboxParserABC(InfoboxElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> InfoboxParsedData: ...

@dataclass(frozen=True)
class WikiTableMapperSet:
    """Registry mapperów tabel (etap translacji parse -> domain)."""

    table_mapper: TableMapperABC | None = None


__all__ = [
    "WikiInfoboxParserABC",
    "WikiListParsedData",
    "WikiListParserABC",
    "WikiSectionParsedData",
    "WikiSectionParserABC",
    "WikiTableMapperSet",
    "WikiTableParsedData",
    "WikiTableParserABC",
]
