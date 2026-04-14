from bs4 import Tag

from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.element_parser_abc import HtmlTagParserABC
from scrapers.parsers.navbox_element_parser import NavboxElementParser
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiElementType


class WikiNavboxParser(HtmlTagParserABC[NavBoxParsedData]):
    element_type: WikiElementType = "navbox"

    def __init__(self, parser: NavboxElementParser | None = None) -> None:
        self._parser = parser or NavboxElementParser()

    def parse(self, raw: Tag) -> NavBoxParsedData:
        return self._parser.parse(raw)


# ``NavBoxParser`` is the canonical public name for this parser.
NavBoxParser = WikiNavboxParser


__all__ = ["NavBoxParser", "WikiNavboxParser", "NavBoxParsedData"]
