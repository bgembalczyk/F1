from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import Literal
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
TagT = TypeVar("TagT", bound=Tag)
PayloadT = TypeVar("PayloadT")

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


class WikiTagParserABC(HtmlTagParserABC[TagOutT], ABC, Generic[TagOutT]):
    """Unified wiki parser contract for bs4.Tag inputs."""

    @abstractmethod
    def parse(self, raw: Tag) -> TagOutT: ...


class WikiElementParserABC(ABC, Generic[TagT, PayloadT]):
    """Canonical wiki parser contract for single HTML elements."""

    @abstractmethod
    def parse(self, raw: TagT) -> PayloadT: ...


class WikiSoupParserABC(HtmlSoupParserABC[SoupOutT], ABC, Generic[SoupOutT]):
    """Unified wiki parser contract for BeautifulSoup inputs."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> SoupOutT: ...


class WikiTableElementParserABC(
    WikiTagParserABC[WikiTableData],
    TableHtmlParserABC[WikiTableData],
    ABC,
):
    element_type: WikiElementType = "table"

    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...


class WikiListElementParserABC(
    WikiTagParserABC[WikiListData],
    ListHtmlParserABC[WikiListData],
    ABC,
):
    element_type: WikiElementType = "list"

    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...


class WikiInfoboxElementParserABC(
    WikiTagParserABC[WikiInfoboxData],
    InfoboxHtmlParserABC[WikiInfoboxData],
    ABC,
):
    element_type: WikiElementType = "infobox"


class WikiNavboxElementParserABC(
    WikiTagParserABC[WikiNavboxData],
    NavboxHtmlParserABC[WikiNavboxData],
    ABC,
):
    element_type: WikiElementType = "navbox"


class WikiFigureElementParserABC(
    WikiTagParserABC[WikiFigureData],
    FigureHtmlParserABC[WikiFigureData],
    ABC,
):
    element_type: WikiElementType = "figure"


class WikiParagraphElementParserABC(
    WikiTagParserABC[ParagraphElementData],
    ParagraphHtmlParserABC[ParagraphElementData],
    ABC,
):
    element_type: WikiElementType = "paragraph"

    @abstractmethod
    def parse(self, raw: Tag) -> ParagraphElementData: ...


class WikiReferencesElementParserABC(
    WikiTagParserABC[ReferencesWrapParsedData],
    ReferencesElementParserABC[ReferencesWrapParsedData],
    ABC,
):
    element_type: WikiElementType = "references"

    @abstractmethod
    def parse(self, raw: Tag) -> ReferencesWrapParsedData: ...


class WikiSectionElementParserABC(
    WikiSoupParserABC[WikiSectionData],
    SectionHtmlParserABC[WikiSectionData],
    ABC,
):
    element_type: WikiElementType = "section"

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> WikiSectionData: ...


class WikiArticleParserABC(
    WikiSoupParserABC[list[dict[str, Any]]],
    ArticleHtmlParserABC[list[dict[str, Any]]],
    ABC,
):
    element_type: WikiElementType = "article"

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> list[dict[str, Any]]: ...


class WikiDocumentParserABC(WikiSectionElementParserABC, ABC):
    """Backward-compatible alias used across contracts."""


class WikiListParserABC(WikiListElementParserABC, ABC):
    """Domain base for tag-based list-like wiki parsers."""


class WikiTableParserABC(WikiTableElementParserABC, WikiListParserABC, ABC):
    """Domain-named table parser base (list-like contract branch)."""


class WikiInfoboxParserABC(WikiInfoboxElementParserABC, WikiListParserABC, ABC):
    """Domain-named infobox parser base (list-like contract branch)."""


class WikiNavboxParserABC(WikiNavboxElementParserABC, WikiListParserABC, ABC):
    """Domain-named navbox parser base (list-like contract branch)."""


class WikiFigureParserABC(WikiFigureElementParserABC, WikiListParserABC, ABC):
    """Domain-named figure parser base (list-like contract branch)."""


class WikiParagraphParserABC(WikiParagraphElementParserABC, WikiListParserABC, ABC):
    """Domain-named paragraph parser base (list-like contract branch)."""


class WikiSectionParserABC(WikiSectionElementParserABC, ABC):
    """Domain-named alias for wiki section/document parsers."""


__all__ = [
    "WikiArticleParserABC",
    "WikiDocumentParserABC",
    "WikiElementParserABC",
    "WikiElementType",
    "WikiFigureElementParserABC",
    "WikiFigureParserABC",
    "WikiInfoboxElementParserABC",
    "WikiInfoboxParserABC",
    "WikiListElementParserABC",
    "WikiListParserABC",
    "WikiNavboxElementParserABC",
    "WikiParagraphElementParserABC",
    "WikiReferencesElementParserABC",
    "WikiSectionElementParserABC",
    "WikiSoupParserABC",
    "WikiTableElementParserABC",
    "WikiTagParserABC",
]
