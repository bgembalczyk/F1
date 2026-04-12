from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.parsers.section.base_section_parser import BaseSectionParser
from scrapers.parsers.season_standings import SeasonStandingsParser
from scrapers.section.parse_results import SectionParseResult
from scrapers.section.serializer import build_section_parse_result

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SeasonDriversStandingsSectionParser(BaseSectionParser):
    def __init__(self, parser: SeasonStandingsParser, season_year: int | None) -> None:
        self._parser = parser
        self._season_year = season_year

    def parse(self, fragment: BeautifulSoup) -> SectionParseResult:
        records = self._parser.parse(
            fragment,
            standings="drivers",
            season_year=self._season_year,
        )
        return build_section_parse_result(
            section_id="World_Drivers'_Championship_standings",
            section_label="Drivers standings",
            records=records,
            parser=self.__class__.__name__,
            source="wikipedia",
            extras={"season_year": self._season_year, "kind": "table"},
        )


__all__ = [
    "SeasonDriversStandingsSectionParser",
]
