from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.html_elements.navbox import NavboxElementParser


class WikiNavboxParser(NavboxElementParser):
    pass


# Backward-compatible alias.
NavBoxParser = WikiNavboxParser

__all__ = ["WikiNavboxParser", "NavBoxParser", "NavBoxParsedData"]
