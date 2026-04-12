from bs4 import Tag

from models.data.parsed.html_elements import InfoboxElementData
from scrapers.parsers.html_elements.infobox import InfoboxElementParser
from scrapers.parsers.wiki.families import WikiInfoboxParserABC


class WikiInfoboxElementParser(WikiInfoboxParserABC, InfoboxElementParser):
    """Wikipedia HTML element parser for infobox tables."""

    def parse(self, raw: Tag) -> InfoboxElementData:
        return super().parse(raw)
