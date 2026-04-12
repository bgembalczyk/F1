from bs4 import Tag

from models.data.wiki.navbox import WikiNavboxData
from scrapers.parsers.navbox_element_parser import NavboxElementParser
from scrapers.parsers.contracts.wiki_elements import WikiNavboxElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiNavboxElementParserABC


class WikiNavboxElementParser(WikiNavboxElementParserABC):
    """Wikipedia HTML element parser for navboxes."""

    def __init__(self, parser: NavboxElementParser | None = None) -> None:
        self._parser = parser or NavboxElementParser()

    def parse(self, raw: Tag) -> WikiNavboxData:
        return self._parser.parse(raw)
