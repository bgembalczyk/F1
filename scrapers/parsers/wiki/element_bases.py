from __future__ import annotations

from abc import ABC

from bs4 import Tag

from models.data.parsed.references_wrap import ReferencesWrapParsedData
from models.data.wiki.figure import WikiFigureData
from models.data.wiki.infobox import WikiInfoboxData
from models.data.wiki.list import WikiListData
from models.data.wiki.navbox import WikiNavboxData
from models.data.wiki.table import WikiTableData
from scrapers.parsers.wiki.wiki_figure_parser_abc import WikiFigureParserABC
from scrapers.parsers.wiki.section_nodes.infobox import WikiInfoboxParserABC
from scrapers.parsers.wiki.section_nodes.list import WikiListParserABC
from scrapers.parsers.wiki.wiki_navbox_parser_abc import WikiNavboxParserABC
from scrapers.parsers.wiki.section_nodes.table import WikiTableParserABC
from scrapers.parsers.wiki.section.base import BaseSectionParser
from scrapers.parsers.contracts.wiki_elements import WikiFigureParserABC
from scrapers.parsers.contracts.wiki_elements import WikiInfoboxParserABC
from scrapers.parsers.contracts.wiki_elements import WikiListParserABC
from scrapers.parsers.contracts.wiki_elements import WikiNavboxParserABC
from scrapers.parsers.contracts.wiki_elements import WikiTableParserABC
from scrapers.parsers.section_parser_abc import SectionParserABC


class _WikiTagDelegatingParserBase(ABC):
    """Common helper for Wikipedia tag-based element parser wrappers."""

    @staticmethod
    def _parse_with_delegate(delegate: object, raw: Tag):
        return delegate.parse(raw)


class WikiTableParserBase(_WikiTagDelegatingParserBase, WikiTableParserABC, ABC):
    pass


class WikiListParserBase(_WikiTagDelegatingParserBase, WikiListParserABC, ABC):
    pass


class WikiInfoboxParserBase(_WikiTagDelegatingParserBase, WikiInfoboxParserABC, ABC):
    pass


class WikiSectionParserBase(BaseSectionParser, ABC):
    """Domain base for section parsers (BeautifulSoup -> SectionParseResult)."""



class WikiNavboxParserBase(_WikiTagDelegatingParserBase, WikiNavboxParserABC, ABC):
    pass


class WikiFigureParserBase(_WikiTagDelegatingParserBase, WikiFigureParserABC, ABC):
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
