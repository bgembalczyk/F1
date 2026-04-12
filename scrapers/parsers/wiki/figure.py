from bs4 import Tag

from models.data.parsed.figure import FigureParsedData
from scrapers.parsers.html_elements.figure import FigureElementParser
from scrapers.parsers.wiki.families import WikiFigureHtmlParserABC


class WikiFigureParser(WikiFigureHtmlParserABC, FigureElementParser):
    def parse(self, raw: Tag) -> FigureParsedData:
        return FigureElementParser.parse(self, raw)


__all__ = ["WikiFigureParser", "FigureParsedData"]
