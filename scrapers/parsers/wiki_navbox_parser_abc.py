from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from scrapers.parsers.element_parser_abc import NavboxElementParserABC
from scrapers.parsers.wiki.types import WikiNavboxData


class WikiNavboxParserABC(NavboxElementParserABC[WikiNavboxData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiNavboxData: ...
