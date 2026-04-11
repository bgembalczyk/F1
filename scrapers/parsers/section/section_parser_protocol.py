from typing import Protocol
from typing import runtime_checkable

from bs4 import BeautifulSoup

from scrapers.parsers.roles import SectionParser
from scrapers.section.parse_results import SectionParseResult


@runtime_checkable
class SectionParserProtocol(SectionParser[SectionParseResult], Protocol):
    def parse(self, fragment: BeautifulSoup) -> SectionParseResult: ...


__all__ = ["SectionParserProtocol"]
