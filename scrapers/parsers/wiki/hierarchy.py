from __future__ import annotations

from scrapers.parsers.contracts.html import TagParserABC as ElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiInfoboxParserABC as InfoboxElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiListParserABC as ListElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiSectionParserABC as SectionElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiTableParserABC as TableElementParserABC

from scrapers.parsers.contracts.wiki_elements import WikiInfoboxParserABC as InfoboxParserABC
from scrapers.parsers.contracts.wiki_elements import WikiListParserABC as ListParserABC
from scrapers.parsers.contracts.wiki_elements import WikiSectionParserABC as SectionParserABC
from scrapers.parsers.contracts.html import SoupParserABC
from scrapers.parsers.contracts.wiki_elements import WikiTableParserABC as TableParserABC
from scrapers.parsers.contracts.html import TagParserABC

WikiParserABC = ElementParserABC

__all__ = [
    "InfoboxParserABC",
    "ListParserABC",
    "SectionParserABC",
    "SoupParserABC",
    "TableParserABC",
    "TagParserABC",
]
