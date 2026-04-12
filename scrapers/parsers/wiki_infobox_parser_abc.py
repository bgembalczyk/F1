from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from scrapers.parsers.tag_parser_abc import HtmlTagParserABC
from scrapers.parsers.wiki.types import WikiInfoboxData


class WikiInfoboxParserABC(HtmlTagParserABC[WikiInfoboxData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiInfoboxData: ...

