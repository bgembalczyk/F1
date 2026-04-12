from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.html_elements.navbox import NavboxElementParser


class WikiNavboxParser(NavboxElementParser):
    pass


__all__ = ["WikiNavboxParser", "NavBoxParsedData"]
