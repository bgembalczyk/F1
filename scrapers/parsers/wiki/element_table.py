from bs4 import Tag

from models.data.wiki.table import WikiTableData
from scrapers.parsers.element_parser_abc import HtmlTagParserABC
from scrapers.parsers.table_element_parser import TableElementParser


class WikiTableElementParser(HtmlTagParserABC[WikiTableData]):
    """Wikipedia HTML element parser for `<table class="wikitable">`."""

    def __init__(self, parser: TableElementParser | None = None) -> None:
        self._parser = parser or TableElementParser()

    def parse(self, raw: Tag) -> WikiTableData:
        return self._parser.parse(raw)
