from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.data.parsed.figure import FigureParsedData
from models.data.parsed.infobox import InfoboxParsedData
from models.data.parsed.nav_box import NavBoxParsedData
from models.data.parsed.references_wrap import ReferencesWrapParsedData
from scrapers.parsers.roles import HtmlElementParserABC

WikiTableParsedData = dict[str, Any]
WikiListParsedData = dict[str, Any]
WikiSectionParsedData = dict[str, Any]


class WikiTableHtmlParserABC(HtmlElementParserABC[WikiTableParsedData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableParsedData: ...


class WikiListHtmlParserABC(HtmlElementParserABC[WikiListParsedData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListParsedData: ...


class WikiSectionHtmlParserABC(ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> WikiSectionParsedData: ...


class WikiInfoboxHtmlParserABC(HtmlElementParserABC[InfoboxParsedData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> InfoboxParsedData: ...


class WikiNavboxHtmlParserABC(HtmlElementParserABC[NavBoxParsedData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> NavBoxParsedData: ...


class WikiFigureHtmlParserABC(HtmlElementParserABC[FigureParsedData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> FigureParsedData: ...


class WikiReferencesHtmlParserABC(HtmlElementParserABC[ReferencesWrapParsedData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> ReferencesWrapParsedData: ...


__all__ = [
    "WikiFigureHtmlParserABC",
    "WikiInfoboxHtmlParserABC",
    "WikiListHtmlParserABC",
    "WikiListParsedData",
    "WikiNavboxHtmlParserABC",
    "WikiReferencesHtmlParserABC",
    "WikiSectionHtmlParserABC",
    "WikiSectionParsedData",
    "WikiTableHtmlParserABC",
    "WikiTableParsedData",
]
