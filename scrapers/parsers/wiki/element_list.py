from bs4 import Tag

from scrapers.parsers.html_elements.list import ListElementParser
from scrapers.parsers.wiki.families import WikiListParserABC
from scrapers.parsers.wiki.types import WikiListData


class WikiListElementParser(WikiListParserABC):
    """Wikipedia HTML element parser for list elements (`ul`/`ol`)."""

    def __init__(self, parser: ListElementParser | None = None) -> None:
        self._parser = parser or ListElementParser()

    def parse(self, raw: Tag) -> WikiListData:
        return self._parser.parse(raw)
