from bs4 import Tag

from scrapers.parsers.contracts.wiki_infobox_parser_abc import WikiInfoboxParserABC
from scrapers.parsers.html_elements.infobox import InfoboxElementParser
from scrapers.parsers.wiki.types import WikiInfoboxData


class WikiInfoboxElementParser(WikiInfoboxParserABC):
    """Wikipedia HTML element parser for infobox tables."""

    def __init__(self, parser: InfoboxElementParser | None = None) -> None:
        self._parser = parser or InfoboxElementParser()

    def parse(self, raw: Tag) -> WikiInfoboxData:
        return self._parser.parse(raw)
