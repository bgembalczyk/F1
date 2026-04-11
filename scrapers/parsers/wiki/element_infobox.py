from bs4 import Tag

from models.data.parsed.html_elements import InfoboxElementData
from scrapers.parsers.html_elements.infobox import InfoboxElementParser


class WikiInfoboxElementParser(InfoboxElementParser):
    """Wikipedia HTML element parser for infobox tables."""

    def parse(self, raw: Tag) -> InfoboxElementData:
        return super().parse(raw)
