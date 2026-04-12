from __future__ import annotations

from abc import ABC
from abc import abstractmethod
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

TagT = TypeVar("TagT", bound=Tag)
SoupT = TypeVar("SoupT", bound=BeautifulSoup)
PayloadT = TypeVar("PayloadT")

WikiElementType = Literal[
    "table",
    "list",
    "section",
    "infobox",
    "navbox",
    "figure",
    "paragraph",
    "references_wrap",
    "article",
]


class WikiElementParserABC(ABC, Generic[TagT, PayloadT]):
    """Canonical wiki parser contract for single HTML elements."""

    element_type: WikiElementType

    @abstractmethod
    def parse(self, raw: TagT) -> PayloadT: ...


class WikiDocumentParserABC(ABC, Generic[SoupT, PayloadT]):
    """Canonical wiki parser contract for soup/document inputs."""

    element_type: WikiElementType

    @abstractmethod
    def parse(self, raw: SoupT) -> PayloadT: ...


class WikiTableElementParserABC(WikiElementParserABC[Tag, WikiTableData], ABC):
    element_type: WikiElementType = "table"


class WikiListElementParserABC(WikiElementParserABC[Tag, WikiListData], ABC):
    element_type: WikiElementType = "list"


class WikiInfoboxElementParserABC(WikiElementParserABC[Tag, WikiInfoboxData], ABC):
    element_type: WikiElementType = "infobox"


class WikiNavboxElementParserABC(WikiElementParserABC[Tag, WikiNavboxData], ABC):
    element_type: WikiElementType = "navbox"


class WikiFigureElementParserABC(WikiElementParserABC[Tag, WikiFigureData], ABC):
    element_type: WikiElementType = "figure"


class WikiParagraphElementParserABC(
    WikiElementParserABC[Tag, ParagraphElementData],
    ABC,
):
    element_type: WikiElementType = "paragraph"


class WikiReferencesElementParserABC(
    WikiElementParserABC[Tag, ReferencesWrapParsedData],
    ABC,
):
    element_type: WikiElementType = "references_wrap"


class WikiSectionElementParserABC(
    WikiDocumentParserABC[BeautifulSoup, WikiSectionData],
    ABC,
):
    element_type: WikiElementType = "section"


class WikiArticleParserABC(
    WikiDocumentParserABC[BeautifulSoup, list[dict[str, object]]],
    ABC,
):
    element_type: WikiElementType = "article"


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
    "PayloadT",
    "SoupT",
    "TagT",
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
    "WikiNavboxParserABC",
    "WikiParagraphElementParserABC",
    "WikiParagraphParserABC",
    "WikiReferencesElementParserABC",
    "WikiSectionElementParserABC",
    "WikiSectionParserABC",
    "WikiTableElementParserABC",
    "WikiTableParserABC",
]
