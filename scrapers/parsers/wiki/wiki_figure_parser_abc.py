from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from models.data.wiki.figure import WikiFigureData
from scrapers.parsers.element_parser_abc import FigureElementParserABC
from scrapers.parsers.tag_parser_abc import TagParserABC


class WikiFigureParserABC(FigureElementParserABC[WikiFigureData], TagParserABC[WikiFigureData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiFigureData: ...
