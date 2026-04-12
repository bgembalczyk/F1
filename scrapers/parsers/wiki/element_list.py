from bs4 import Tag

from scrapers.parsers.contracts.wiki_list_parser_abc import WikiListParserABC
from scrapers.parsers.html_elements.list_element_parser import ListElementParser
from scrapers.parsers.wiki.types import WikiListData


class WikiListElementParser(WikiListParserABC):
    """Wikipedia HTML element parser for list elements (`ul`/`ol`)."""

    def __init__(self, parser: ListElementParser | None = None) -> None:
        self._parser = parser or ListElementParser()

    def parse(self, raw: Tag) -> WikiListData:
        return self._parser.parse(raw)
