from bs4 import Tag

from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.html_elements.navbox import NavboxElementParser


class WikiNavboxParser(WikiNavboxHtmlParserABC, NavboxElementParser):
    def parse(self, raw: Tag) -> NavBoxParsedData:
        return NavboxElementParser.parse(self, raw)


__all__ = ["WikiNavboxParser", "NavBoxParsedData"]
