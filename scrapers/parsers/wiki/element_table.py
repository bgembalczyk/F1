from bs4 import Tag

from scrapers.parsers.table_element_parser import TableElementParser
from scrapers.parsers.wiki.types import WikiTableData
from scrapers.parsers.wiki_table_parser_abc import WikiTableParserABC


class WikiTableElementParser(WikiTableParserABC):
    """Wikipedia HTML element parser for `<table class="wikitable">`."""

    def __init__(self, parser: TableElementParser | None = None) -> None:
        self._parser = parser or TableElementParser()

    def parse(self, raw: Tag) -> WikiTableData:
        return self._parser.parse(raw)
