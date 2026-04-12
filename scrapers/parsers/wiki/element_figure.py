from bs4 import Tag

from scrapers.parsers.contracts.wiki_figure_parser_abc import WikiFigureParserABC
from scrapers.parsers.html_elements.figure_element_parser import FigureElementParser
from scrapers.parsers.wiki.types import WikiFigureData


class WikiFigureElementParser(WikiFigureParserABC):
    """Wikipedia HTML element parser for `<figure>` elements."""

    def __init__(self, parser: FigureElementParser | None = None) -> None:
        self._parser = parser or FigureElementParser()

    def parse(self, raw: Tag) -> WikiFigureData:
        return self._parser.parse(raw)
