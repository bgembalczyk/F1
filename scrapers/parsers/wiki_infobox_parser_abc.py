from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from scrapers.parsers.element_parser_abc import InfoboxElementParserABC
from scrapers.parsers.infobox_parser_abc import InfoboxParserABC
from scrapers.parsers.wiki.types import WikiInfoboxData


class WikiInfoboxParserABC(InfoboxParserABC, InfoboxElementParserABC[WikiInfoboxData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiInfoboxData: ...
