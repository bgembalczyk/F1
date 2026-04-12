from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from scrapers.parsers.element_parser_abc import ListElementParserABC
from scrapers.parsers.wiki.types import WikiListData


class WikiListParserABC(ListElementParserABC[WikiListData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...
