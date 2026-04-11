from __future__ import annotations

from bs4 import Tag

from models.data.parsed.html_elements import InfoboxElementData
from scrapers.infobox.parsers.html import InfoboxHtmlParser
from scrapers.parsers.html_elements.infobox import InfoboxElementParser


class LegacyInfoboxHtmlParserAdapter(InfoboxElementParser):
    """Adapter exposing legacy InfoboxHtmlParser through new element parser contract."""

    def __init__(self, parser: InfoboxHtmlParser | None = None) -> None:
        self._parser = parser or InfoboxHtmlParser()

    def parse(self, element: Tag) -> InfoboxElementData:
        return self._parser.parse_element(element)
