from bs4 import Tag

from models.data.parsed.html_elements import FigureElementData
from scrapers.parsers.html_elements.figure import FigureElementParser


class WikiFigureElementParser(FigureElementParser):
    """Wikipedia HTML element parser for `<figure>` elements."""

    def parse(self, raw: Tag) -> FigureElementData:
        return super().parse(raw)
