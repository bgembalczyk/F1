from bs4 import Tag

from models.data.parsed.html_elements import TableElementData
from scrapers.parsers.html_elements.base import BaseHtmlElementParser
from scrapers.parsers.table.wiki.table import WikiTableParser


class TableElementParser(BaseHtmlElementParser[TableElementData]):
    def __init__(self, table_parser: WikiTableParser | None = None) -> None:
        self._table_parser = table_parser or WikiTableParser()

    def parse(self, element: Tag) -> TableElementData:
        return self._table_parser.parse(element)
