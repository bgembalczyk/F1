from bs4 import Tag

from models.data.wiki.figure import WikiFigureData
from scrapers.parsers.figure_element_parser import FigureElementParser
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiFigureElementParserABC


class WikiFigureElementParser(WikiFigureElementParserABC):
    """Wikipedia HTML element parser for `<figure>` elements."""

    def __init__(self, parser: FigureElementParser | None = None) -> None:
        self._parser = parser or FigureElementParser()

    def parse(self, raw: Tag) -> WikiFigureData:
        return self._parser.parse(raw)
