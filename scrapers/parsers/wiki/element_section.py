from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.parsers.html_elements.section import SectionElementParser
from scrapers.parsers.wiki.families import WikiSectionStructureParserABC
from scrapers.parsers.wiki.types import WikiSectionData


class WikiSectionElementParser(WikiSectionStructureParserABC):
    """Wikipedia HTML element parser for section containers."""

    def __init__(self, parser: SectionElementParser | None = None) -> None:
        self._parser = parser or SectionElementParser()

    def parse(self, raw: BeautifulSoup | Tag | list[Tag]) -> WikiSectionData:
        return self._parser.parse(raw)
