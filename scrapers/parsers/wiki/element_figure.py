from bs4 import Tag

from models.data.wiki.figure import WikiFigureData
from scrapers.parsers.figure_element_parser import FigureElementParser
from scrapers.parsers.wiki_figure_parser_abc import WikiFigureParserABC


class WikiFigureElementParser(WikiFigureParserABC):
    """Wikipedia HTML element parser for `<figure>` elements."""

    def __init__(self, parser: FigureElementParser | None = None) -> None:
        self._parser = parser or FigureElementParser()

    def parse(self, raw: Tag) -> WikiFigureData:
        return self._parser.parse(raw)
