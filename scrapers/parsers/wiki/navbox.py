from bs4 import Tag

from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.contracts.wiki_elements import WikiNavboxElementParserABC
from scrapers.parsers.navbox_element_parser import NavboxElementParser


class WikiNavboxParser(WikiNavboxElementParserABC):
    def __init__(self, parser: NavboxElementParser | None = None) -> None:
        self._parser = parser or NavboxElementParser()

    def parse(self, raw: Tag) -> NavBoxParsedData:
        return self._parser.parse(raw)


# ``NavBoxParser`` is the canonical public name for this parser.
NavBoxParser = WikiNavboxParser


__all__ = ["NavBoxParser", "WikiNavboxParser", "NavBoxParsedData"]
