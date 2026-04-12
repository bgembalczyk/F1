from bs4 import Tag

from models.data.parsed.figure import FigureParsedData
from scrapers.parsers.html_elements.figure import FigureElementParser


class WikiFigureParser(FigureElementParser):
    pass


__all__ = ["WikiFigureParser", "FigureParsedData"]
