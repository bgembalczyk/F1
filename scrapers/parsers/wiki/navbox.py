from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.html_elements.navbox import NavboxElementParser


class NavBoxParser(NavboxElementParser):
    pass


__all__ = ["NavBoxParser", "NavBoxParsedData"]
