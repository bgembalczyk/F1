from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.interface import SectionParseResult

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.seasons.parsers.calendar import SeasonCalendarParser


class SeasonCalendarSectionParser:
    def __init__(self, parser: SeasonCalendarParser, season_year: int | None) -> None:
        self._parser = parser
        self._season_year = season_year

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records = self._parser.parse(section_fragment, self._season_year)
        return SectionParseResult(
            section_id="Calendar",
            section_label="Calendar",
            records=records,
            metadata={"season_year": self._season_year, "kind": "table"},
        )
