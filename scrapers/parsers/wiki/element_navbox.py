from bs4 import Tag

from models.data.wiki.navbox import WikiNavboxData
from scrapers.parsers.navbox_element_parser import NavboxElementParser
from scrapers.parsers.wiki.element_bases import WikiNavboxParserBase


class WikiNavboxElementParser(WikiNavboxParserBase):
    """Wikipedia HTML element parser for navboxes."""

    def __init__(self, parser: NavboxElementParser | None = None) -> None:
        self._parser = parser or NavboxElementParser()

    def parse(self, raw: Tag) -> WikiNavboxData:
        return self._parse_with_delegate(self._parser, raw)
