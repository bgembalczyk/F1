from models.data.parsed.figure import FigureParsedData
from scrapers.parsers.html_elements.figure import FigureElementParser


class WikiFigureParser(FigureElementParser):
    pass


# Backward-compatible alias.
FigureParser = WikiFigureParser

__all__ = ["WikiFigureParser", "FigureParser", "FigureParsedData"]
