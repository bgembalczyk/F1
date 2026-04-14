from bs4 import Tag

from models.data.wiki.navbox import WikiNavboxData
from scrapers.parsers.element_parser_abc import HtmlTagParserABC
from scrapers.parsers.navbox_element_parser import NavboxElementParser
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiElementType


class WikiNavboxElementParser(HtmlTagParserABC[WikiNavboxData]):
    """Wikipedia HTML element parser for navboxes."""

    element_type: WikiElementType = "navbox"

    def __init__(self, parser: NavboxElementParser | None = None) -> None:
        self._parser = parser or NavboxElementParser()

    def parse(self, raw: Tag) -> WikiNavboxData:
        return self._parser.parse(raw)
