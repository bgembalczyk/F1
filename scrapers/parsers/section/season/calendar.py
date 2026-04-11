from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.parsers.seasons.calendar import SeasonCalendarParser
from scrapers.parsers.section.base import BaseSectionParser
from scrapers.parsers.roles import SectionParserABC
from scrapers.section.parse_results import SectionParseResult
from scrapers.section.serializer import build_section_parse_result

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SeasonCalendarSectionParser(BaseSectionParser):
    def __init__(self, parser: SeasonCalendarParser, season_year: int | None) -> None:
        self._parser = parser
        self._season_year = season_year

    def parse(self, fragment: BeautifulSoup) -> SectionParseResult:
        records = self._parser.parse(fragment, self._season_year)
        return build_section_parse_result(
            section_id="Calendar",
            section_label="Calendar",
            records=records,
            parser=self.__class__.__name__,
            source="wikipedia",
            extras={"season_year": self._season_year, "kind": "table"},
        )


__all__ = ["SeasonCalendarSectionParser"]
