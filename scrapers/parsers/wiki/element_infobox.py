from bs4 import Tag

from models.data.wiki.infobox import WikiInfoboxData
from scrapers.parsers.infobox_element_parser import InfoboxElementParser
from scrapers.parsers.wiki.element_bases import WikiInfoboxParserBase


class WikiInfoboxElementParser(WikiInfoboxParserBase):
    """Wikipedia HTML element parser for infobox tables."""

    def __init__(self, parser: InfoboxElementParser | None = None) -> None:
        self._parser = parser or InfoboxElementParser()

    def parse(self, raw: Tag) -> WikiInfoboxData:
        return self._parse_with_delegate(self._parser, raw)
