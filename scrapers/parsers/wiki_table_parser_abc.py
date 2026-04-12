from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from models.data.wiki.table import WikiTableData
from scrapers.parsers.element_parser_abc import TableElementParserABC


class WikiTableParserABC(TableElementParserABC[WikiTableData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...
