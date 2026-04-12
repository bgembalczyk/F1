from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from models.data.wiki.list import WikiListData
from scrapers.parsers.element_parser_abc import ListElementParserABC


class WikiListParserABC(ListElementParserABC[WikiListData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...
