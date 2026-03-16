from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.sections.interface import SectionParseResult
from scrapers.seasons.parsers.standings import SeasonStandingsParser


class SeasonDriversStandingsSectionParser:
    def __init__(self, parser: SeasonStandingsParser, season_year: int | None) -> None:
        self._parser = parser
        self._season_year = season_year

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records = self._parser.parse_drivers(section_fragment, self._season_year)
        return SectionParseResult(
            section_id="World_Drivers'_Championship_standings",
            section_label="Drivers standings",
            records=records,
            metadata={"season_year": self._season_year, "kind": "table"},
        )


class SeasonConstructorsStandingsSectionParser:
    def __init__(self, parser: SeasonStandingsParser) -> None:
        self._parser = parser

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records = self._parser.parse_constructors(section_fragment)
        return SectionParseResult(
            section_id="World_Constructors'_Championship_standings",
            section_label="Constructors standings",
            records=records,
            metadata={"kind": "table"},
        )
