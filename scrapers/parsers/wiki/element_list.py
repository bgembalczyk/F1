from bs4 import Tag

from models.data.wiki.list import WikiListData
from scrapers.parsers.list_element_parser import ListElementParser
from scrapers.parsers.contracts.wiki_elements import WikiListParserABC

class WikiListElementParser(WikiListParserABC):
    """Wikipedia HTML element parser for list elements (`ul`/`ol`)."""

    def __init__(self, parser: ListElementParser | None = None) -> None:
        self._parser = parser or ListElementParser()

    def parse(self, raw: Tag) -> WikiListData:
        return self._parser.parse(raw)
