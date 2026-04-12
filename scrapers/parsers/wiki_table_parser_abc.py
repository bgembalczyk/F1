from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from scrapers.parsers.tag_parser_abc import TagParserABC
from scrapers.parsers.wiki.types import WikiTableData


class WikiTableParserABC(TagParserABC[WikiTableData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...
