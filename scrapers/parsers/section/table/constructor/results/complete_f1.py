from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.parsers.section.table.constructor.base import (
    ConstructorTablesSectionParser,
)
from scrapers.section.parse_results import SectionParseResult


class ConstructorCompleteF1ResultsSectionParser(ConstructorTablesSectionParser):
    def __init__(self) -> None:
        super().__init__(
            section_id="complete_formula_one_results",
            section_label="Complete F1 results",
        )

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        return super().parse(section_fragment)


__all__ = ["ConstructorCompleteF1ResultsSectionParser"]
