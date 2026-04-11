from models.data.parsed.figure import FigureParsedData
from scrapers.parsers.html_elements.figure import FigureElementParser


class FigureParser(FigureElementParser):
    pass


__all__ = ["FigureParser", "FigureParsedData"]
