from scrapers.parsers.table.wiki.table import WikiTableHtmlParser
from scrapers.parsers.wiki.families import WikiTableHtmlParserABC


class WikiTableParser(WikiTableHtmlParserABC, WikiTableHtmlParser):
    """Wiki parser for wikitable elements (<table class=\"wikitable\">)."""


__all__ = ["WikiTableParser"]
