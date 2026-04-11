from bs4 import Tag

from models.data.parsed.html_elements import ListElementData
from scrapers.parsers.html_elements.list import ListElementParser


class WikiListElementParser(ListElementParser):
    """Wikipedia HTML element parser for list elements (`ul`/`ol`)."""

    def parse(self, raw: Tag) -> ListElementData:
        return super().parse(raw)
