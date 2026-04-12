from bs4 import Tag

from models.data.wiki.table import WikiTableData
from scrapers.parsers.table_element_parser import TableElementParser
from scrapers.parsers.wiki.element_bases import WikiTableParserBase


class WikiTableElementParser(WikiTableParserBase):
    """Wikipedia HTML element parser for `<table class="wikitable">`."""

    def __init__(self, parser: TableElementParser | None = None) -> None:
        self._parser = parser or TableElementParser()

    def parse(self, raw: Tag) -> WikiTableData:
        return self._parse_with_delegate(self._parser, raw)
