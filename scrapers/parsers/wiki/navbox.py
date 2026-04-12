from bs4 import Tag

from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.navbox_element_parser import NavboxElementParser
from scrapers.parsers.wiki_navbox_parser_abc import WikiNavboxParserABC


class WikiNavboxParser(WikiNavboxParserABC):
    def __init__(self, parser: NavboxElementParser | None = None) -> None:
        self._parser = parser or NavboxElementParser()

    def parse(self, raw: Tag) -> NavBoxParsedData:
        return self._parser.parse(raw)


__all__ = ["WikiNavboxParser", "NavBoxParsedData"]
