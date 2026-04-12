from abc import ABC
from abc import abstractmethod

from bs4 import BeautifulSoup

from models.data.wiki.section import WikiSectionData
from scrapers.parsers.element_parser_abc import SectionElementParserABC
from scrapers.parsers.parser_abc import ParserABC


class WikiSectionParserABC(
    SectionElementParserABC[WikiSectionData],
    ParserABC[BeautifulSoup, WikiSectionData],
    ABC,
):
    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> WikiSectionData: ...
