from models.data.parsed.infobox import InfoboxParsedData
from scrapers.parsers.html_elements.infobox import InfoboxElementParser


class InfoboxParser(InfoboxElementParser):
    pass


__all__ = ["InfoboxParser", "InfoboxParsedData"]
