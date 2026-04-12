from bs4 import Tag

from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.html_elements.navbox import NavboxElementParser
from scrapers.parsers.wiki.families import WikiNavboxHtmlParserABC


class WikiNavboxParser(WikiNavboxHtmlParserABC, NavboxElementParser):
    def parse(self, raw: Tag) -> NavBoxParsedData:
        return NavboxElementParser.parse(self, raw)


__all__ = ["WikiNavboxParser", "NavBoxParsedData"]
