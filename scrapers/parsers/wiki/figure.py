from bs4 import Tag

from models.data.parsed.figure import FigureParsedData
from scrapers.parsers.contracts.wiki_elements import WikiFigureElementParserABC
from scrapers.parsers.figure_element_parser import FigureElementParser


class WikiFigureParser(WikiFigureElementParserABC):
    def __init__(self, parser: FigureElementParser | None = None) -> None:
        self._parser = parser or FigureElementParser()

    def parse(self, raw: Tag) -> FigureParsedData:
        return self._parser.parse(raw)


__all__ = ["WikiFigureParser", "FigureParsedData"]
