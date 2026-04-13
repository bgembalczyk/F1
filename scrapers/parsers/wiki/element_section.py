from bs4 import BeautifulSoup

from models.data.wiki.section import WikiSectionData
from scrapers.parsers.element_parser_abc import HtmlSoupParserABC
from scrapers.parsers.section_element_parser import SectionElementParser


class WikiSectionElementParser(HtmlSoupParserABC[WikiSectionData]):
    """Wikipedia HTML element parser for section containers."""

    def __init__(self, parser: SectionElementParser | None = None) -> None:
        self._parser = parser or SectionElementParser()

    def parse(self, raw: BeautifulSoup) -> WikiSectionData:
        return self._parser.parse(raw)
