from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.calendar_circuit import CalendarCircuitColumn
from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.season_date import SeasonDateColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.tyre import TyreColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.seasons.parsers.season_table_parser import SeasonTableParser


class SeasonCalendarParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self, soup: BeautifulSoup, season_year: int | None
    ) -> List[Dict[str, Any]]:
        return self._table_parser.parse_table(
            soup,
            section_ids=["Calendar"],
            expected_headers=["Round", "Grand Prix", "Circuit", "Race date"],
            column_map={
                "Round": "round",
                "Grand Prix": "grand_prix",
                "Circuit": "circuit",
                "Race date": "race_date",
            },
            columns={
                "round": IntColumn(),
                "grand_prix": UrlColumn(),
                "circuit": CalendarCircuitColumn(),
                "race_date": SeasonDateColumn(year=season_year),
            },
        )


class SeasonResultsParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._table_parser.parse_table(
            soup,
            section_ids=["Grands_Prix"],
            expected_headers=[
                "Round",
                "Grand Prix",
                "Pole position",
                "Fastest lap",
                "Winning driver",
                "Winning constructor",
                "Report",
            ],
            column_map={
                "Round": "round",
                "Grand Prix": "grand_prix",
                "Pole position": "pole_position",
                "Fastest lap": "fastest_lap",
                "Winning driver": "winning_driver",
                "Winning constructor": "winning_constructor",
                "Report": "report",
                "Tyre": "tyre",
            },
            columns={
                "round": IntColumn(),
                "grand_prix": UrlColumn(),
                "pole_position": DriverColumn(),
                "fastest_lap": DriverColumn(),
                "winning_driver": DriverColumn(),
                "winning_constructor": ConstructorColumn(),
                "report": UrlColumn(),
                "tyre": TyreColumn(),
            },
        )


class SeasonNonChampionshipParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self, soup: BeautifulSoup, season_year: int | None
    ) -> List[Dict[str, Any]]:
        return self._table_parser.parse_table(
            soup,
            section_ids=["Non-championship_races", "Non-championship_race"],
            expected_headers=[
                "Race name",
                "Circuit",
                "Date",
                "Winning driver",
                "Constructor",
                "Report",
            ],
            column_map={
                "Race name": "race_name",
                "Circuit": "circuit",
                "Date": "date",
                "Winning driver": "winning_driver",
                "Constructor": "constructor",
                "Report": "report",
            },
            columns={
                "race_name": TextColumn(),
                "circuit": UrlColumn(),
                "date": SeasonDateColumn(year=season_year),
                "winning_driver": DriverColumn(),
                "constructor": ConstructorColumn(),
                "report": UrlColumn(),
            },
        )


class SeasonScoringSystemParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._table_parser.parse_table(
            soup,
            section_ids=["Scoring_system", "Points_scoring_system"],
            expected_headers=["Position", "1st", "2nd", "3rd", "4th", "5th"],
            column_map={
                "Position": "position",
            },
            columns={
                "position": TextColumn(),
            },
            default_column=IntColumn(),
        )


class SeasonStandingsParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse_drivers(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._parse_standings_table(
            soup,
            section_ids=[
                "World_Drivers'_Championship_standings",
                "World_Championship_of_Drivers_standings",
            ],
            subject_header="Driver",
            subject_key="driver",
            subject_column=DriverColumn(),
        )

    def parse_constructors(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._parse_standings_table(
            soup,
            section_ids=[
                "World_Constructors'_Championship_standings",
                "International_Cup_for_F1_Constructors_standings",
            ],
            subject_header="Constructor",
            subject_key="constructor",
            subject_column=ConstructorColumn(),
        )

    def _parse_standings_table(
        self,
        soup: BeautifulSoup,
        *,
        section_ids: list[str],
        subject_header: str,
        subject_key: str,
        subject_column: Any,
    ) -> List[Dict[str, Any]]:
        return self._table_parser.parse_standings_table(
            soup,
            section_ids=section_ids,
            subject_header=subject_header,
            subject_key=subject_key,
            subject_column=subject_column,
        )


class SeasonRegionalChampionshipParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self, soup: BeautifulSoup, *, section_ids: list[str], season_year: int | None
    ) -> List[Dict[str, Any]]:
        return self._table_parser.parse_table(
            soup,
            section_ids=section_ids,
            expected_headers=[
                "Race name",
                "Circuit",
                "Date",
                "Winning driver",
                "Constructor",
                "Report",
            ],
            column_map={
                "Race name": "race_name",
                "Circuit": "circuit",
                "Date": "date",
                "Winning driver": "winning_driver",
                "Constructor": "constructor",
                "Report": "report",
            },
            columns={
                "race_name": TextColumn(),
                "circuit": UrlColumn(),
                "date": SeasonDateColumn(year=season_year),
                "winning_driver": DriverColumn(),
                "constructor": ConstructorColumn(),
                "report": UrlColumn(),
            },
        )
