from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from models.data.wiki.infobox import WikiInfoboxData
from scrapers.parsers.element_parser_abc import InfoboxElementParserABC
from scrapers.parsers.infobox_parser_abc import InfoboxParserABC


class WikiInfoboxParserABC(InfoboxParserABC, InfoboxElementParserABC[WikiInfoboxData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiInfoboxData: ...
