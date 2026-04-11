"""Canonical exports for wiki HTML element parsers."""

from scrapers.infobox.parsers.html import WikiInfoboxHtmlParser
from scrapers.parsers.table.wiki.table import WikiTableHtmlParser
from scrapers.parsers.wiki.base import WikiTableElementParserBase
from scrapers.parsers.wiki.infobox import WikiInfoboxElementParserBase

__all__ = [
    "WikiInfoboxElementParserBase",
    "WikiInfoboxHtmlParser",
    "WikiTableElementParserBase",
    "WikiTableHtmlParser",
]
