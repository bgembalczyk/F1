from __future__ import annotations

from abc import ABC

from bs4 import Tag

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


class _WikiTagDelegatingParserBase(ABC):
    """Common helper for Wikipedia tag-based element parser wrappers."""

    @staticmethod
    def _parse_with_delegate(delegate: object, raw: Tag):
        return delegate.parse(raw)


class WikiTableParserBase(_WikiTagDelegatingParserBase, WikiTableElementParserABC, ABC):
    pass


class WikiListParserBase(_WikiTagDelegatingParserBase, WikiListElementParserABC, ABC):
    pass


class WikiInfoboxParserBase(_WikiTagDelegatingParserBase, WikiInfoboxElementParserABC, ABC):
    pass


class WikiSectionParserBase(BaseSectionParser, ABC):
    """Domain base for section parsers (BeautifulSoup -> SectionParseResult)."""


class WikiNavboxParserBase(_WikiTagDelegatingParserBase, WikiNavboxElementParserABC, ABC):
    pass


class WikiFigureParserBase(_WikiTagDelegatingParserBase, WikiFigureElementParserABC, ABC):
    pass


class WikiReferencesParserBase(_WikiTagDelegatingParserBase, ABC):
    def parse(self, raw: Tag) -> ReferencesWrapParsedData: ...


__all__ = [
    "WikiFigureData",
    "WikiFigureParserBase",
    "WikiInfoboxData",
    "WikiInfoboxParserBase",
    "WikiListData",
    "WikiListParserBase",
    "WikiNavboxData",
    "WikiNavboxParserBase",
    "WikiReferencesParserBase",
    "WikiSectionParserBase",
    "WikiTableData",
    "WikiTableParserBase",
]
