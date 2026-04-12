from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.parsers.section.table.constructor import ConstructorTablesSectionParser
from scrapers.section.parse_results import SectionParseResult


class ConstructorChampionshipResultsSectionParser(ConstructorTablesSectionParser):
    def __init__(self) -> None:
        super().__init__(
            section_id="championship_results",
            section_label="Championship results",
        )

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        return super().parse(section_fragment)


__all__ = ["ConstructorChampionshipResultsSectionParser"]
