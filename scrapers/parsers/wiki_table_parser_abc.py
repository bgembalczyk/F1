from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from scrapers.parsers.element_parser_abc import TableElementParserABC
from scrapers.parsers.wiki.types import WikiTableData


class WikiTableParserABC(TableElementParserABC[WikiTableData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...
