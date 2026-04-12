from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import Literal

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.parsers.constants_contracts import SoupOut
from scrapers.parsers.constants_contracts import TagOut
from scrapers.parsers.parser_abc import ParserABC

ElementType = Literal[
    "table",
    "list",
    "section",
    "infobox",
    "navbox",
    "references",
    "references_wrap",
    "paragraph",
    "figure",
]


class HtmlTagParserABC(ParserABC[Tag, TagOut], ABC, Generic[TagOut]):
    """Canonical parser contract for single bs4.Tag inputs."""

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...


class HtmlSoupParserABC(ParserABC[BeautifulSoup, SoupOut], ABC, Generic[SoupOut]):
    """Canonical parser contract for BeautifulSoup inputs."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> SoupOut: ...


class TableHtmlParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "table"


class ListHtmlParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "list"


class SectionHtmlParserABC(HtmlSoupParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "section"


class InfoboxHtmlParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "infobox"


class NavboxHtmlParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "navbox"


class ParagraphHtmlParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "paragraph"


class FigureHtmlParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "figure"


class HtmlElementParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType


class ReferencesElementParserABC(HtmlElementParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "references"
