from abc import ABC
from abc import abstractmethod

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.parsers.contracts.parser_abc import ParserABC
from scrapers.parsers.wiki.types import WikiSectionData


class WikiSectionParserABC(ParserABC[BeautifulSoup | Tag | list[Tag], WikiSectionData], ABC):
    @abstractmethod
    def parse(self, raw: BeautifulSoup | Tag | list[Tag]) -> WikiSectionData: ...

