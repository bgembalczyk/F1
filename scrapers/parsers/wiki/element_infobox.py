from bs4 import Tag

from models.data.wiki.infobox import WikiInfoboxData
from scrapers.parsers.infobox_element_parser import InfoboxElementParser
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiInfoboxElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiInfoboxParserABC


class WikiInfoboxElementParser(WikiInfoboxElementParserABC):
    """Wikipedia HTML element parser for infobox tables."""

    def __init__(self, parser: InfoboxElementParser | None = None) -> None:
        self._parser = parser or InfoboxElementParser()

    def parse(self, raw: Tag) -> WikiInfoboxData:
        return self._parser.parse(raw)
