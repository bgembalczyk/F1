from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.serializer import build_section_parse_result

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.sections.interface import SectionParseResult
    from scrapers.seasons.parsers.standings import SeasonStandingsParser


class SeasonDriversStandingsSectionParser:
    def __init__(self, parser: SeasonStandingsParser, season_year: int | None) -> None:
        self._parser = parser
        self._season_year = season_year

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records = self._parser.parse_drivers(section_fragment, self._season_year)
        return build_section_parse_result(
            section_id="World_Drivers'_Championship_standings",
            section_label="Drivers standings",
            records=records,
            parser=self.__class__.__name__,
            source="wikipedia",
            extras={"season_year": self._season_year, "kind": "table"},
        )


class SeasonConstructorsStandingsSectionParser:
    def __init__(self, parser: SeasonStandingsParser) -> None:
        self._parser = parser

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records = self._parser.parse_constructors(section_fragment)
        return build_section_parse_result(
            section_id="World_Constructors'_Championship_standings",
            section_label="Constructors standings",
            records=records,
            parser=self.__class__.__name__,
            source="wikipedia",
            extras={"kind": "table"},
        )
