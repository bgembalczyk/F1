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
from models.data.wiki.table import WikiTableData
from scrapers.parsers.contracts.wiki_elements import WikiArticleParserABC
from scrapers.parsers.contracts.wiki_elements import WikiFigureParserABC
from scrapers.parsers.contracts.wiki_elements import WikiInfoboxParserABC
from scrapers.parsers.contracts.wiki_elements import WikiListParserABC
from scrapers.parsers.contracts.wiki_elements import WikiNavboxParserABC
from scrapers.parsers.contracts.wiki_elements import WikiParagraphParserABC
from scrapers.parsers.contracts.wiki_elements import WikiTableParserABC
from scrapers.parsers.contracts.wiki_elements import WikiFigureElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiInfoboxElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiListElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiNavboxElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiParagraphElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiReferencesElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiTableElementParserABC
from scrapers.parsers.wiki.section.base import BaseSectionParser

HtmlInputT = TypeVar("HtmlInputT", Tag, BeautifulSoup)
OutputT = TypeVar("OutputT")


class WikiDelegatingHtmlParserBase(ABC, Generic[HtmlInputT, OutputT]):
    """Single delegating base for wiki HTML element parsers."""

    def __init__(self, delegate: object | None = None) -> None:
        self._delegate = delegate

    @abstractmethod
    def parse(self, raw: HtmlInputT) -> OutputT: ...

    def _parse_with_delegate(self, raw: HtmlInputT) -> OutputT:
        if self._delegate is None:
            msg = "Delegate parser is required for delegated parsing."
            raise RuntimeError(msg)
        return self._delegate.parse(raw)


class WikiTableParserBase(WikiDelegatingHtmlParserBase[Tag, WikiTableData], WikiTableElementParserABC, ABC):
    pass


class WikiListParserBase(WikiDelegatingHtmlParserBase[Tag, WikiListData], WikiListElementParserABC, ABC):
    pass


class WikiInfoboxParserBase(WikiDelegatingHtmlParserBase[Tag, WikiInfoboxData], WikiInfoboxElementParserABC, ABC):
    pass


class WikiNavboxParserBase(WikiDelegatingHtmlParserBase[Tag, WikiNavboxData], WikiNavboxElementParserABC, ABC):
    pass


class WikiFigureParserBase(WikiDelegatingHtmlParserBase[Tag, WikiFigureData], WikiFigureElementParserABC, ABC):
    pass


class WikiParagraphParserBase(
    WikiDelegatingHtmlParserBase[Tag, ParagraphElementData],
    WikiParagraphElementParserABC,
    ABC,
):
    pass


class WikiReferencesParserBase(
    WikiDelegatingHtmlParserBase[Tag, ReferencesWrapParsedData],
    WikiReferencesElementParserABC,
    ABC,
):
    pass


class WikiArticleParserBase(
    WikiDelegatingHtmlParserBase[BeautifulSoup, list[dict[str, Any]]],
    WikiArticleParserABC,
    ABC,
):
    pass


class WikiSectionParserBase(BaseSectionParser, ABC):
    """Domain base for section parsers (BeautifulSoup -> SectionParseResult)."""


__all__ = [
    "WikiArticleParserBase",
    "WikiDelegatingHtmlParserBase",
    "WikiFigureData",
    "WikiFigureParserBase",
    "WikiInfoboxData",
    "WikiInfoboxParserBase",
    "WikiListData",
    "WikiListParserBase",
    "WikiNavboxData",
    "WikiNavboxParserBase",
    "WikiParagraphParserBase",
    "WikiReferencesParserBase",
    "WikiSectionParserBase",
    "WikiTableData",
    "WikiTableParserBase",
]
