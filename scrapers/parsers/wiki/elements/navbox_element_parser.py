from bs4 import Tag

from models.data.parsed.html_elements import NavboxElementData
from scrapers.parsers.html_elements.navbox import NavboxElementParser
from scrapers.parsers.wiki.elements.abc import WikiNavboxHtmlParserABC


class WikiNavboxElementParser(WikiNavboxHtmlParserABC, NavboxElementParser):
    """Wikipedia HTML element parser for navboxes."""

    def parse(self, raw: Tag) -> NavboxElementData:
        return super().parse(raw)
