from __future__ import annotations

from scrapers.parsers.wiki.families import WikiElementParserABC as ElementParserABC
from scrapers.parsers.wiki.families import WikiInfoboxParserABC as InfoboxElementParserABC
from scrapers.parsers.wiki.families import WikiListParserABC as ListElementParserABC
from scrapers.parsers.wiki.families import WikiSectionParserABC as SectionElementParserABC
from scrapers.parsers.wiki.families import WikiTableParserABC as TableElementParserABC

WikiParserABC = ElementParserABC

__all__ = [
    "ElementParserABC",
    "InfoboxElementParserABC",
    "ListElementParserABC",
    "SectionElementParserABC",
    "TableElementParserABC",
    "WikiParserABC",
]
