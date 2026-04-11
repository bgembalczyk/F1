from models.data.parsed.list import ListParsedData
from scrapers.parsers.html_elements.list import ListElementParser


class ListParser(ListElementParser):
    pass


__all__ = ["ListParser", "ListParsedData"]
