from scrapers.parsers.table.table.table import WikiTableHtmlParser
from scrapers.parsers.wiki.families import WikiTableParserABC


class WikiTableParser(WikiTableParserABC):
    """Wiki parser for wikitable elements (<table class=\"wikitable\">)."""


__all__ = ["WikiTableParser"]
