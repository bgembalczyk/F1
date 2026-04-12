from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from scrapers.parsers.contracts.html import TagParserABC
from scrapers.parsers.wiki.types import WikiInfoboxData


class WikiInfoboxParserABC(TagParserABC[WikiInfoboxData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiInfoboxData: ...

