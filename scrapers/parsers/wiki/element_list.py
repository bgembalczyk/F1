from bs4 import Tag

from models.data.wiki.list import WikiListData
from scrapers.parsers.list_element_parser import ListElementParser
from scrapers.parsers.wiki.element_bases import WikiListParserBase


class WikiListElementParser(WikiListParserBase):
    """Wikipedia HTML element parser for list elements (`ul`/`ol`)."""

    def __init__(self, parser: ListElementParser | None = None) -> None:
        self._parser = parser or ListElementParser()

    def parse(self, raw: Tag) -> WikiListData:
        return self._parse_with_delegate(self._parser, raw)
