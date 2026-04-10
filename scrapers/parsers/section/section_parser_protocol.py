from typing import Protocol
from typing import runtime_checkable

from bs4 import BeautifulSoup

from scrapers.section.parse_results import SectionParseResult


@runtime_checkable
class SectionParserProtocol(Protocol):
    def parse(self, fragment: BeautifulSoup) -> SectionParseResult: ...


__all__ = ["SectionParserProtocol"]
