from bs4 import Tag

from models.data.parsed.figure import FigureParsedData
from scrapers.parsers.contracts.wiki_figure_parser_abc import WikiFigureParserABC
from scrapers.parsers.html_elements.figure_element_parser import FigureElementParser


class WikiFigureParser(WikiFigureParserABC):
    def __init__(self, parser: FigureElementParser | None = None) -> None:
        self._parser = parser or FigureElementParser()

    def parse(self, raw: Tag) -> FigureParsedData:
        return self._parser.parse(raw)


__all__ = ["WikiFigureParser", "FigureParsedData"]
