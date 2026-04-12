from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import Literal

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.parsers.constants_contracts import TagOut
from scrapers.parsers.tag_parser_abc import HtmlTagParserABC
from scrapers.parsers.soup_parser_abc import HtmlSoupParserABC

ElementType = Literal[
    "table",
    "list",
    "section",
    "infobox",
    "navbox",
    "references",
    "paragraph",
    "figure",
]


class TableHtmlParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    """Domain family: parser of HTML table-like payloads from a Tag input."""

    element_type: ElementType = "table"

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...


class ListHtmlParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    """Domain family: parser of HTML list payloads from a Tag input."""

    element_type: ElementType = "list"

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...


class SectionHtmlParserABC(HtmlSoupParserABC[TagOut], ABC, Generic[TagOut]):
    """Domain family: parser of HTML sections from BeautifulSoup inputs."""

    element_type: ElementType = "section"

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> TagOut: ...


class InfoboxHtmlParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    """Domain family: parser of HTML infobox payloads from a Tag input."""

    element_type: ElementType = "infobox"

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...


class NavboxHtmlParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    """Domain family: parser of HTML navbox payloads from a Tag input."""

    element_type: ElementType = "navbox"

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...


class ParagraphHtmlParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    """Domain family: parser of HTML paragraph payloads from a Tag input."""

    element_type: ElementType = "paragraph"

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...


class HtmlElementParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    """Backward-compatible generic HTML element layer for tag-based elements."""

    element_type: ElementType

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...


#: Backward-compatible alias — use HtmlElementParserABC for new generic code.
ElementParserABC = HtmlElementParserABC


class ListElementParserABC(ListHtmlParserABC[TagOut], ABC, Generic[TagOut]):
    pass


class TableElementParserABC(TableHtmlParserABC[TagOut], ABC, Generic[TagOut]):
    pass


class InfoboxElementParserABC(InfoboxHtmlParserABC[TagOut], ABC, Generic[TagOut]):
    pass


class SectionElementParserABC(SectionHtmlParserABC[TagOut], ABC, Generic[TagOut]):
    pass


class NavboxElementParserABC(NavboxHtmlParserABC[TagOut], ABC, Generic[TagOut]):
    pass


class ReferencesElementParserABC(HtmlElementParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "references"


class ParagraphElementParserABC(ParagraphHtmlParserABC[TagOut], ABC, Generic[TagOut]):
    pass


class FigureElementParserABC(HtmlElementParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "figure"
