from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.parsers.section.table.constructor.base import (
    ConstructorTablesSectionParser,
)
from scrapers.section.parse_results import SectionParseResult


class ConstructorHistorySectionParser(ConstructorTablesSectionParser):
    def __init__(self) -> None:
        super().__init__(section_id="history", section_label="History")

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        return super().parse(section_fragment)


__all__ = ["ConstructorHistorySectionParser"]
