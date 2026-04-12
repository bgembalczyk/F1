from bs4 import BeautifulSoup

from models.data.parsed.html_elements import SectionElementData
from scrapers.parsers.html_elements.section import SectionElementParser
from scrapers.parsers.wiki.families import WikiSectionParserABC


class WikiSectionElementParser(WikiSectionParserABC, SectionElementParser):
    """Wikipedia HTML element parser for section containers."""

    def parse(self, raw: BeautifulSoup) -> SectionElementData:
        return super().parse(raw)
