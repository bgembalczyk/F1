from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from models.data.wiki.navbox import WikiNavboxData
from scrapers.parsers.element_parser_abc import NavboxElementParserABC


class WikiNavboxParserABC(NavboxElementParserABC[WikiNavboxData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiNavboxData: ...
