from typing import Protocol
from typing import runtime_checkable

from bs4 import BeautifulSoup

from scrapers.family_contracts import SectionParserContract
from scrapers.section.parse_results import SectionParseResult


@runtime_checkable
class SectionParser(SectionParserContract, Protocol):
    """Common section parser interface.

    Input: BeautifulSoup fragment scoped to a section.
    Output: parsed records with section-level metadata.
    """

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult: ...


__all__ = ["SectionParserProtocol"]
