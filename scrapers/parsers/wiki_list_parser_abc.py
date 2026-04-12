from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from scrapers.parsers.contracts.soup_parser_abc import TagParserABC
from scrapers.parsers.wiki.types import WikiListData


class WikiListParserABC(TagParserABC[WikiListData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...
