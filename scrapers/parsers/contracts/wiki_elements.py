from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.parsers.contracts.base import ParserABC
from scrapers.parsers.contracts.html import TagParserABC
from scrapers.parsers.wiki.types import WikiFigureData
from scrapers.parsers.wiki.types import WikiInfoboxData
from scrapers.parsers.wiki.types import WikiListData
from scrapers.parsers.wiki.types import WikiNavboxData
from scrapers.parsers.wiki.types import WikiSectionData
from scrapers.parsers.wiki.types import WikiTableData

FieldValue = TypeVar("FieldValue")


class WikiTableParserABC(TagParserABC[WikiTableData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...


class WikiListParserABC(TagParserABC[WikiListData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...


class WikiSectionParserABC(ParserABC[BeautifulSoup | Tag | list[Tag], WikiSectionData], ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup | Tag | list[Tag]) -> WikiSectionData: ...


class WikiInfoboxParserABC(TagParserABC[WikiInfoboxData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiInfoboxData: ...


class WikiNavboxParserABC(TagParserABC[WikiNavboxData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiNavboxData: ...


class WikiFigureParserABC(TagParserABC[WikiFigureData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiFigureData: ...


class InfoboxFieldParserABC(TagParserABC[FieldValue], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> FieldValue: ...


class WikiSectionStructureParserABC(WikiSectionParserABC, ABC):
    """Compatibility branch for section structure parsers."""

@dataclass(frozen=True)
class WikiTableMapperSet:
    """Registry mapperów tabel (etap translacji parse -> domain)."""

    table_mapper: Any = None


__all__ = [
    "WikiFigureParserABC",
    "WikiInfoboxParserABC",
    "WikiListParserABC",
    "WikiNavboxParserABC",
    "WikiSectionParserABC",
    "WikiSectionStructureParserABC",
    "WikiTableMapperSet",
    "WikiTableParserABC",
    "InfoboxFieldParserABC",
    "FieldValue",
]
