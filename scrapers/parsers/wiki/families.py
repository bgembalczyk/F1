from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from bs4 import BeautifulSoup
from bs4 import Tag

from typing import Any
from scrapers.parsers.wiki.types import WikiFigureData
from scrapers.parsers.wiki.types import WikiInfoboxData
from scrapers.parsers.wiki.types import WikiListData
from scrapers.parsers.wiki.types import WikiNavboxData
from scrapers.parsers.wiki.types import WikiSectionData
from scrapers.parsers.wiki.types import WikiTableData


class WikiElementParserABC(ABC):
    """Wspólny pionowy kontrakt parserów elementów wiki."""


class WikiTableParserABC(WikiElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...


class WikiListParserABC(WikiElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...


class WikiSectionParserABC(WikiElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup | Tag | list[Tag]) -> WikiSectionData: ...


class WikiInfoboxParserABC(WikiElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiInfoboxData: ...


class WikiNavboxParserABC(WikiElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiNavboxData: ...


class WikiFigureParserABC(WikiElementParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiFigureData: ...


class WikiSectionStructureParserABC(WikiSectionParserABC, ABC):
    """Backward-compatible alias branch for section structure parsers."""


# Backward-compatible aliases
WikiNavboxHtmlParserABC = WikiNavboxParserABC
WikiFigureHtmlParserABC = WikiFigureParserABC


@dataclass(frozen=True)
class WikiTableMapperSet:
    """Registry mapperów tabel (etap translacji parse -> domain)."""

    table_mapper: Any = None


__all__ = [
    "WikiElementParserABC",
    "WikiFigureParserABC",
    "WikiFigureHtmlParserABC",
    "WikiInfoboxParserABC",
    "WikiListParserABC",
    "WikiNavboxParserABC",
    "WikiNavboxHtmlParserABC",
    "WikiSectionParserABC",
    "WikiSectionStructureParserABC",
    "WikiTableMapperSet",
    "WikiTableParserABC",
]
