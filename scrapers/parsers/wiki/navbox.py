from bs4 import Tag

from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.contracts.wiki_elements import WikiNavboxParserABC
from scrapers.parsers.html_elements.navbox import NavboxElementParser


class WikiNavboxParser(WikiNavboxParserABC):
    def __init__(self, parser: NavboxElementParser | None = None) -> None:
        self._parser = parser or NavboxElementParser()

    def parse(self, raw: Tag) -> NavBoxParsedData:
        return self._parser.parse(raw)


__all__ = ["WikiNavboxParser", "NavBoxParsedData"]
