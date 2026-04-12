from bs4 import BeautifulSoup

from models.data.wiki.section import WikiSectionData
from scrapers.parsers.contracts.wiki_elements import WikiSectionElementParserABC
from scrapers.parsers.section_element_parser import SectionElementParser
from scrapers.parsers.wiki.wiki_section_structure_parser_abc import WikiSectionStructureParserABC


class WikiSectionElementParser(WikiSectionStructureParserABC):
    """Wikipedia HTML element parser for section containers."""

    def __init__(self, parser: SectionElementParser | None = None) -> None:
        self._parser = parser or SectionElementParser()

    def parse(self, raw: BeautifulSoup) -> WikiSectionData:
        return self._parser.parse(raw)
