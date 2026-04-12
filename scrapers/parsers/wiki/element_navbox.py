from bs4 import Tag

from scrapers.parsers.contracts.wiki_elements import WikiNavboxParserABC
from scrapers.parsers.html_elements.navbox import NavboxElementParser
from scrapers.parsers.wiki.types import WikiNavboxData


class WikiNavboxElementParser(WikiNavboxParserABC):
    """Wikipedia HTML element parser for navboxes."""

    def __init__(self, parser: NavboxElementParser | None = None) -> None:
        self._parser = parser or NavboxElementParser()

    def parse(self, raw: Tag) -> WikiNavboxData:
        return self._parser.parse(raw)
