from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from scrapers.parsers.tag_parser_abc import HtmlTagParserABC
from scrapers.parsers.wiki.types import WikiListData


class WikiListParserABC(HtmlTagParserABC[WikiListData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...
