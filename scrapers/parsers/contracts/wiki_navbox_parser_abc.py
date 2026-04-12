from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from scrapers.parsers.contracts.html import TagParserABC
from scrapers.parsers.wiki.types import WikiNavboxData


class WikiNavboxParserABC(TagParserABC[WikiNavboxData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiNavboxData: ...

