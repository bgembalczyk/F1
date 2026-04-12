from bs4 import Tag

from models.data.parsed.html_elements import TableElementData
from scrapers.parsers.element_parser_abc import TableElementParserABC
from scrapers.parsers.wiki.table.table import WikiTableHtmlParser
from scrapers.parsers.wiki_table_parser_abc import WikiTableParserABC


class TableElementParser(WikiTableParserABC, TableElementParserABC[TableElementData]):
    def __init__(self, table_parser: WikiTableHtmlParser | None = None) -> None:
        self._table_parser = table_parser or WikiTableHtmlParser()

    def parse(self, raw: Tag) -> TableElementData:
        return self._table_parser.parse(raw)
