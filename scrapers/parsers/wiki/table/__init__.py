from scrapers.parsers.wiki.table.table import WikiTableHtmlParser


class WikiTableParser(WikiTableHtmlParser):
    """Wiki parser for wikitable elements (<table class="wikitable">)."""


__all__ = ["WikiTableParser"]
