from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Literal

from bs4 import BeautifulSoup
from bs4 import Tag

from models.data.parsed.html_elements import ParagraphElementData
from models.data.wiki.figure import WikiFigureData
from models.data.wiki.infobox import WikiInfoboxData
from models.data.wiki.list import WikiListData
from models.data.wiki.navbox import WikiNavboxData
from models.data.wiki.section import WikiSectionData
from models.data.wiki.table import WikiTableData
from scrapers.parsers.element_parser_abc import HtmlSoupParserABC
from scrapers.parsers.element_parser_abc import HtmlTagParserABC

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
    HtmlTagParserABC[WikiTableData],
    ABC,
):
    element_type: WikiElementType = "table"

    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...


class WikiListElementParserABC(
    HtmlTagParserABC[WikiListData],
    ABC,
):
    element_type: WikiElementType = "list"

    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...


class WikiInfoboxElementParserABC(
    HtmlTagParserABC[WikiInfoboxData],
    ABC,
):
    element_type: WikiElementType = "infobox"


class WikiNavboxElementParserABC(
    HtmlTagParserABC[WikiNavboxData],
    ABC,
):
    element_type: WikiElementType = "navbox"


class WikiFigureElementParserABC(
    HtmlTagParserABC[WikiFigureData],
    ABC,
):
    element_type: WikiElementType = "figure"


class WikiParagraphElementParserABC(
    HtmlTagParserABC[ParagraphElementData],
    ABC,
):
    element_type: WikiElementType = "paragraph"

    @abstractmethod
    def parse(self, raw: Tag) -> ParagraphElementData: ...


class WikiArticleParserABC(
    HtmlSoupParserABC[list[dict[str, Any]]],
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
    "WikiTableElementParserABC",
]
