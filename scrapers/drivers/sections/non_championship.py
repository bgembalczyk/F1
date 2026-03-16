from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.sections.interface import SectionParseResult
from scrapers.drivers.sections.results import DriverResultsSectionParser


class DriverNonChampionshipSectionParser:
    SECTION_ID = "Non-championship"
    HEADER_ALIASES = ("Non-championship", "Non-championship races")

    def __init__(self, *, parser: DriverResultsSectionParser) -> None:
        self._parser = parser

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        parsed = self._parser.parse(section_fragment)
        return SectionParseResult(
            section_id=self.SECTION_ID,
            section_label="Non-championship",
            records=parsed.records,
            metadata={"aliases": self.HEADER_ALIASES},
        )
