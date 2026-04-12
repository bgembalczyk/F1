from scrapers.parsers.wiki.tables.html_table_element_parser import WikiTableHtmlParser
from scrapers.parsers.wiki.elements.abc import WikiTableHtmlParserABC


class WikiTableParser(WikiTableHtmlParserABC):
    """Wiki parser for wikitable elements (<table class=\"wikitable\">)."""


__all__ = ["WikiTableParser"]
