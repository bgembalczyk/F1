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
from scrapers.parsers.contracts.wiki_elements import WikiFigureElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiInfoboxElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiListElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiNavboxElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiTableElementParserABC
from scrapers.parsers.wiki.section.base import BaseSectionParser
from scrapers.parsers.wiki.section.base import BaseSectionParser
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiArticleParserABC
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiFigureParserABC
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiInfoboxParserABC
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiListParserABC
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiNavboxParserABC
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiParagraphParserABC
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiTableParserABC

HtmlInputT = TypeVar("HtmlInputT", Tag, BeautifulSoup)
OutputT = TypeVar("OutputT")


class WikiDelegatingHtmlParserBase(ABC, Generic[HtmlInputT, OutputT]):
    """Single delegating base for wiki HTML element parsers."""

    def __init__(self, delegate: object) -> None:
        self._delegate = delegate

    @abstractmethod
    def parse(self, raw: HtmlInputT) -> OutputT: ...

    def _parse_with_delegate(self, raw: HtmlInputT) -> OutputT:
        return self._delegate.parse(raw)


class WikiTableParserBase(WikiDelegatingHtmlParserBase[Tag, WikiTableData], WikiTableParserABC, ABC):
    pass


class WikiListParserBase(WikiDelegatingHtmlParserBase[Tag, WikiListData], WikiListParserABC, ABC):
    pass


class WikiInfoboxParserBase(WikiDelegatingHtmlParserBase[Tag, WikiInfoboxData], WikiInfoboxParserABC, ABC):
    pass


class WikiNavboxParserBase(WikiDelegatingHtmlParserBase[Tag, WikiNavboxData], WikiNavboxParserABC, ABC):
    pass


class WikiFigureParserBase(WikiDelegatingHtmlParserBase[Tag, WikiFigureData], WikiFigureParserABC, ABC):
    pass


class WikiParagraphParserBase(
    WikiDelegatingHtmlParserBase[Tag, ParagraphElementData],
    WikiParagraphParserABC,
    ABC,
):
    pass


class WikiReferencesParserBase(WikiDelegatingHtmlParserBase[Tag, ReferencesWrapParsedData], ABC):
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
