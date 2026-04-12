from bs4 import Tag

from models.data.parsed.html_elements import TableElementData
from scrapers.parsers.wiki.table.html import WikiTableHtmlParser
from scrapers.parsers.contracts.wiki_elements import WikiTableParserABC


class TableElementParser(WikiTableParserABC):
    def __init__(self, table_parser: WikiTableHtmlParser | None = None) -> None:
        self._table_parser = table_parser or WikiTableHtmlParser()

    def parse(self, raw: Tag) -> TableElementData:
        return self._table_parser.parse(raw)
