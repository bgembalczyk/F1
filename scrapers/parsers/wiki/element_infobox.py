from bs4 import Tag

from models.data.wiki.infobox import WikiInfoboxData
from scrapers.parsers.contracts.wiki_elements import WikiInfoboxElementParserABC
from scrapers.parsers.infobox_element_parser import InfoboxElementParser


class WikiInfoboxElementParser(WikiInfoboxElementParserABC):
    """Wikipedia HTML element parser for infobox tables."""

    def __init__(self, parser: InfoboxElementParser | None = None) -> None:
        self._parser = parser or InfoboxElementParser()

    def parse(self, raw: Tag) -> WikiInfoboxData:
        return self._parser.parse(raw)
