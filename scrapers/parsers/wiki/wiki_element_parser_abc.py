from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.data.parsed.html_elements import ParagraphElementData
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
from scrapers.parsers.element_parser_abc import SectionHtmlParserABC
from scrapers.parsers.element_parser_abc import TableHtmlParserABC

class WikiTagDomainParserABC(ABC):
    """Wiki-domain parser contract for bs4.Tag inputs."""

    @abstractmethod
    def parse(self, raw: Tag) -> Any: ...


class WikiSoupDomainParserABC(ABC):
    """Wiki-domain parser contract for BeautifulSoup inputs."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> Any: ...


class WikiTableElementParserABC(
    WikiTagDomainParserABC,
    TableHtmlParserABC[WikiTableData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...


class WikiListElementParserABC(
    WikiTagDomainParserABC,
    ListHtmlParserABC[WikiListData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...


class WikiInfoboxElementParserABC(
    WikiTagDomainParserABC,
    InfoboxHtmlParserABC[WikiInfoboxData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiInfoboxData: ...


class WikiNavboxElementParserABC(
    WikiTagDomainParserABC,
    NavboxHtmlParserABC[WikiNavboxData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiNavboxData: ...


class WikiFigureElementParserABC(
    WikiTagDomainParserABC,
    FigureHtmlParserABC[WikiFigureData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiFigureData: ...


__all__ = [
    "WikiArticleElementParserABC",
    "WikiArticleParserABC",
    "WikiFigureElementParserABC",
    "WikiInfoboxElementParserABC",
    "WikiListElementParserABC",
    "WikiNavboxElementParserABC",
    "WikiSectionElementParserABC",
    "WikiTableElementParserABC",
    "WikiNavboxParserABC",
    "WikiParagraphElementParserABC",
    "WikiParagraphParserABC",
    "WikiSectionElementParserABC",
    "WikiSectionParserABC",
    "WikiSoupDomainParserABC",
    "WikiTableElementParserABC",
    "WikiTableParserABC",
    "WikiTagDomainParserABC",
]
