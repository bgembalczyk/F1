from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.html_elements.navbox import NavboxElementParser
from scrapers.parsers.wiki.elements.abc import WikiNavboxHtmlParserABC


class WikiNavboxParser(WikiNavboxHtmlParserABC, NavboxElementParser):
    pass


__all__ = ["WikiNavboxParser", "NavBoxParsedData"]
