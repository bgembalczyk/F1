from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Literal

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
from scrapers.parsers.element_parser_abc import InfoboxHtmlParserABC
from scrapers.parsers.element_parser_abc import ListHtmlParserABC
from scrapers.parsers.element_parser_abc import NavboxHtmlParserABC
from scrapers.parsers.element_parser_abc import ParagraphHtmlParserABC
from scrapers.parsers.element_parser_abc import ReferencesElementParserABC
from scrapers.parsers.element_parser_abc import SectionHtmlParserABC
from scrapers.parsers.element_parser_abc import TableHtmlParserABC

WikiElementType = Literal[
    "table",
    "list",
    "section",
    "infobox",
    "navbox",
    "references",
    "references_wrap",
    "paragraph",
    "figure",
    "article",
]


class WikiTableElementParserABC(
    TableHtmlParserABC[WikiTableData],
    ABC,
):
    element_type: WikiElementType = "table"

    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...


class WikiListElementParserABC(
    ListHtmlParserABC[WikiListData],
    ABC,
):
    element_type: WikiElementType = "list"

    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...


class WikiInfoboxElementParserABC(
    InfoboxHtmlParserABC[WikiInfoboxData],
    ABC,
):
    element_type: WikiElementType = "infobox"


class WikiNavboxElementParserABC(
    NavboxHtmlParserABC[WikiNavboxData],
    ABC,
):
    element_type: WikiElementType = "navbox"


class WikiFigureElementParserABC(
    FigureHtmlParserABC[WikiFigureData],
    ABC,
):
    element_type: WikiElementType = "figure"


class WikiParagraphElementParserABC(
    ParagraphHtmlParserABC[ParagraphElementData],
    ABC,
):
    element_type: WikiElementType = "paragraph"

    @abstractmethod
    def parse(self, raw: Tag) -> ParagraphElementData: ...


class WikiReferencesElementParserABC(
    ReferencesElementParserABC[ReferencesWrapParsedData],
    ABC,
):
    element_type: WikiElementType = "references"

    @abstractmethod
    def parse(self, raw: Tag) -> ReferencesWrapParsedData: ...


class WikiSectionElementParserABC(
    SectionHtmlParserABC[WikiSectionData],
    ABC,
):
    element_type: WikiElementType = "section"

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> WikiSectionData: ...


class WikiArticleParserABC(
    ArticleHtmlParserABC[list[dict[str, Any]]],
    ABC,
):
    element_type: WikiElementType = "article"

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> list[dict[str, Any]]: ...


__all__ = [
    "WikiArticleParserABC",
    "WikiElementType",
    "WikiFigureElementParserABC",
    "WikiInfoboxElementParserABC",
    "WikiListElementParserABC",
    "WikiNavboxElementParserABC",
    "WikiParagraphElementParserABC",
    "WikiReferencesElementParserABC",
    "WikiSectionElementParserABC",
    "WikiTableElementParserABC",
]
