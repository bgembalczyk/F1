from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.data.parsed.infobox import InfoboxParsedData
from scrapers.parsers.roles import InfoboxHtmlParserABC
from scrapers.parsers.roles import ListHtmlParserABC
from scrapers.parsers.roles import ParserABC
from scrapers.parsers.roles import TableHtmlParserABC
from scrapers.parsers.roles import TableMapperABC

WikiTableParsedData = dict[str, Any]
WikiListParsedData = dict[str, Any]
WikiSectionParsedData = dict[str, Any]


class WikiTableParserABC(TableHtmlParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableParsedData: ...


class WikiListParserABC(ListHtmlParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListParsedData: ...


class WikiSectionParserABC(ParserABC[BeautifulSoup | Tag, WikiSectionParsedData], ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup | Tag) -> WikiSectionParsedData: ...


class WikiInfoboxParserABC(InfoboxHtmlParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> InfoboxParsedData: ...


# Backward-compatible alias during migration.
WikiSectionStructureParserABC = WikiSectionParserABC


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
    "WikiSectionStructureParserABC",
    "WikiTableMapperSet",
    "WikiTableParsedData",
    "WikiTableParserABC",
]
