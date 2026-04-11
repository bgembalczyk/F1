from models.data.parsed.figure import FigureParsedData
from scrapers.parsers.html_elements.figure import FigureElementParser
from scrapers.parsers.wiki.families import WikiFigureHtmlParserABC


class WikiFigureParser(WikiFigureHtmlParserABC, FigureElementParser):
    pass


__all__ = ["WikiFigureParser", "FigureParsedData"]
