from bs4 import Tag

from scrapers.parsers.contracts.wiki_table_parser_abc import WikiTableParserABC
from scrapers.parsers.html_elements.table import TableElementParser
from scrapers.parsers.wiki.types import WikiTableData


class WikiTableElementParser(WikiTableParserABC):
    """Wikipedia HTML element parser for `<table class="wikitable">`."""

    def __init__(self, parser: TableElementParser | None = None) -> None:
        self._parser = parser or TableElementParser()

    def parse(self, raw: Tag) -> WikiTableData:
        return self._parser.parse(raw)
