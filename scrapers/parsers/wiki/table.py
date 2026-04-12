from scrapers.parsers.table.table.table import WikiTableHtmlParser
from scrapers.parsers.wiki.families import WikiTableParserABC
from scrapers.parsers.wiki.table.table import WikiTableHtmlParser
from scrapers.parsers.wiki.families import WikiTableHtmlParserABC


class WikiTableParser(WikiTableParserABC):
    """Wiki parser for wikitable elements (<table class=\"wikitable\">)."""


__all__ = ["WikiTableParser"]
