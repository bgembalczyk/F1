from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from scrapers.parsers.contracts import TagParserABC
from scrapers.parsers.wiki.types import WikiFigureData


class WikiFigureParserABC(TagParserABC[WikiFigureData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiFigureData: ...

