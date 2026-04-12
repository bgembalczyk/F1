from __future__ import annotations

from scrapers.parsers.wiki.families import WikiElementParserABC as ElementParserABC
from scrapers.parsers.wiki.families import WikiInfoboxParserABC as InfoboxElementParserABC
from scrapers.parsers.wiki.families import WikiListParserABC as ListElementParserABC
from scrapers.parsers.wiki.families import WikiSectionParserABC as SectionElementParserABC
from scrapers.parsers.wiki.families import WikiTableParserABC as TableElementParserABC

from scrapers.parsers.base_family import InfoboxParserABC
from scrapers.parsers.base_family import ListParserABC
from scrapers.parsers.base_family import SectionParserABC
from scrapers.parsers.base_family import SoupParserABC
from scrapers.parsers.base_family import TableParserABC
from scrapers.parsers.base_family import TagParserABC

WikiParserABC = ElementParserABC

__all__ = [
    "InfoboxParserABC",
    "ListParserABC",
    "SectionParserABC",
    "SoupParserABC",
    "TableParserABC",
    "TagParserABC",
]
