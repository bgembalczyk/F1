from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from models.data.parsed.html_elements import ParagraphElementData
from models.data.parsed.references_wrap import ReferencesWrapParsedData
from models.data.wiki.figure import WikiFigureData
from models.data.wiki.infobox import WikiInfoboxData
from models.data.wiki.list import WikiListData
from models.data.wiki.navbox import WikiNavboxData
from models.data.wiki.section import WikiSectionData
from models.data.wiki.table import WikiTableData
from scrapers.parsers.element_parser_abc import ArticleHtmlParserABC
from scrapers.parsers.element_parser_abc import FigureHtmlParserABC
from scrapers.parsers.element_parser_abc import HtmlSoupParserABC
from scrapers.parsers.element_parser_abc import HtmlTagParserABC
from scrapers.parsers.element_parser_abc import InfoboxHtmlParserABC
from scrapers.parsers.element_parser_abc import ListHtmlParserABC
from scrapers.parsers.element_parser_abc import NavboxHtmlParserABC
from scrapers.parsers.element_parser_abc import ParagraphHtmlParserABC
from scrapers.parsers.element_parser_abc import ReferencesElementParserABC
from scrapers.parsers.element_parser_abc import SectionHtmlParserABC
from scrapers.parsers.element_parser_abc import TableHtmlParserABC

TagOutT = TypeVar("TagOutT")
SoupOutT = TypeVar("SoupOutT")


class WikiTagParserABC(HtmlTagParserABC[TagOutT], ABC, Generic[TagOutT]):
    """Unified wiki parser contract for bs4.Tag inputs."""

    @abstractmethod
    def parse(self, raw: Tag) -> TagOutT: ...


class WikiSoupParserABC(HtmlSoupParserABC[SoupOutT], ABC, Generic[SoupOutT]):
    """Unified wiki parser contract for BeautifulSoup inputs."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> SoupOutT: ...


class WikiTableElementParserABC(
    WikiTagParserABC[WikiTableData],
    TableHtmlParserABC[WikiTableData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...


class WikiListElementParserABC(
    WikiTagParserABC[WikiListData],
    ListHtmlParserABC[WikiListData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...


class WikiInfoboxElementParserABC(
    WikiTagParserABC[WikiInfoboxData],
    InfoboxHtmlParserABC[WikiInfoboxData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiInfoboxData: ...


class WikiNavboxElementParserABC(
    WikiTagParserABC[WikiNavboxData],
    NavboxHtmlParserABC[WikiNavboxData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiNavboxData: ...


class WikiFigureElementParserABC(
    WikiTagParserABC[WikiFigureData],
    FigureHtmlParserABC[WikiFigureData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiFigureData: ...


class WikiParagraphElementParserABC(
    WikiTagParserABC[ParagraphElementData],
    ParagraphHtmlParserABC[ParagraphElementData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: Tag) -> ParagraphElementData: ...


class WikiReferencesElementParserABC(
    WikiTagParserABC[ReferencesWrapParsedData],
    ReferencesElementParserABC[ReferencesWrapParsedData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: Tag) -> ReferencesWrapParsedData: ...


class WikiSectionElementParserABC(
    WikiSoupParserABC[WikiSectionData],
    SectionHtmlParserABC[WikiSectionData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> WikiSectionData: ...


class WikiArticleParserABC(
    WikiSoupParserABC[list[dict[str, Any]]],
    ArticleHtmlParserABC[list[dict[str, Any]]],
    ABC,
):
    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> list[dict[str, Any]]: ...


__all__ = [
    "WikiArticleParserABC",
    "WikiFigureElementParserABC",
    "WikiInfoboxElementParserABC",
    "WikiListElementParserABC",
    "WikiNavboxElementParserABC",
    "WikiParagraphElementParserABC",
    "WikiReferencesElementParserABC",
    "WikiSectionElementParserABC",
    "WikiSoupParserABC",
    "WikiTableElementParserABC",
    "WikiTagParserABC",
]
