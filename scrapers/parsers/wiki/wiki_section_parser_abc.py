from abc import ABC
from abc import abstractmethod

from bs4 import BeautifulSoup
from bs4 import Tag

from models.data.wiki.section import WikiSectionData
from scrapers.parsers.element_parser_abc import SectionElementParserABC
from scrapers.parsers.parser_abc import ParserABC


class WikiSectionParserABC(
    SectionElementParserABC[WikiSectionData],
    ParserABC[BeautifulSoup | Tag | list[Tag], WikiSectionData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: BeautifulSoup | Tag | list[Tag]) -> WikiSectionData: ...
