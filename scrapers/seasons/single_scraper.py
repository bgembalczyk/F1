from __future__ import annotations

import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions, init_scraper_options
from scrapers.base.scraper import F1Scraper
from scrapers.base.table.columns.types.calendar_circuit import CalendarCircuitColumn
from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.driver_rounds import DriversWithRoundsColumn
from scrapers.base.table.columns.types.engine import EngineColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.points import PointsColumn
from scrapers.base.table.columns.types.position import PositionColumn
from scrapers.base.table.columns.types.race_result import RaceResultColumn
from scrapers.base.table.columns.types.season_date import SeasonDateColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.tyre import TyreColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline
from scrapers.seasons.standings_scraper import F1StandingsScraper


class SingleSeasonScraper(F1Scraper):
    _SKIP = object()

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        season_year: int | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        options.with_fetcher()
        super().__init__(options=options)
        self.url: str = ""
        self.season_year = season_year
        self._options = options

    def fetch_by_url(self, url: str, *, season_year: int | None = None) -> List[Dict[str, Any]]:
        self.url = url
        if season_year is not None:
            self.season_year = season_year
        elif self.season_year is None:
            self.season_year = self._extract_year_from_url(url)
        return super().fetch()

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return [
            {
                "entries": self._parse_entries(soup),
                "free_practice_drivers": self._parse_free_practice(soup),
                "calendar": self._parse_calendar(soup),
                "results": self._parse_results(soup),
                "non_championship_races": self._parse_non_championship(soup),
                "scoring_system": self._parse_scoring_system(soup),
                "drivers_standings": self._parse_drivers_standings(soup),
                "constructors_standings": self._parse_constructors_standings(soup),
                "south_african_formula_one_championship": self._parse_regional_championship(
                    soup, ["South_African_Formula_One_Championship"]
                ),
                "british_formula_one_championship": self._parse_regional_championship(
                    soup, ["British_Formula_One_Championship"]
                ),
            }
        ]

    def _parse_entries(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._parse_table(
            soup,
            section_ids=[
                "Entries",
                "Teams_and_drivers",
                "Drivers_and_constructors",
            ],
            expected_headers=["Entrant", "Constructor", "Chassis"],
            column_map={
                "Entrant": "entrant",
                "Constructor": "constructor",
                "Chassis": "chassis",
                "Power Unit": "power_unit",
                "Power unit": "power_unit",
                "Race drivers": "race_drivers",
                "Race driver(s)": "race_drivers",
                "No.": "no",
                "Engine": "engine",
                "Tyre": "tyre",
            },
            columns={
                "entrant": LinksListColumn(),
                "constructor": ConstructorColumn(),
                "chassis": LinksListColumn(),
                "power_unit": EngineColumn(),
                "race_drivers": DriversWithRoundsColumn(),
                "no": IntColumn(),
                "engine": EngineColumn(),
                "tyre": TyreColumn(),
            },
        )

    def _parse_free_practice(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._parse_table(
            soup,
            section_ids=["Free_practice_drivers"],
            expected_headers=["Constructor", "Practice drivers"],
            column_map={
                "Constructor": "constructor",
                "Practice drivers": "practice_drivers",
                "Practice driver(s)": "practice_drivers",
            },
            columns={
                "constructor": ConstructorColumn(),
                "practice_drivers": DriversWithRoundsColumn(),
            },
        )

    def _parse_calendar(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._parse_table(
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
                "race_date": SeasonDateColumn(year=self.season_year),
            },
        )

    def _parse_results(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._parse_table(
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

    def _parse_non_championship(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._parse_table(
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
                "date": SeasonDateColumn(year=self.season_year),
                "winning_driver": DriverColumn(),
                "constructor": ConstructorColumn(),
                "report": UrlColumn(),
            },
        )

    def _parse_scoring_system(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._parse_table(
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

    def _parse_drivers_standings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
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

    def _parse_constructors_standings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
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

    def _parse_regional_championship(
        self, soup: BeautifulSoup, section_ids: list[str]
    ) -> List[Dict[str, Any]]:
        return self._parse_table(
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
                "date": SeasonDateColumn(year=self.season_year),
                "winning_driver": DriverColumn(),
                "constructor": ConstructorColumn(),
                "report": UrlColumn(),
            },
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
        for section_id in section_ids:
            config = ScraperConfig(
                url=self.url,
                section_id=section_id,
                expected_headers=[subject_header],
                column_map={
                    "Pos.": "pos",
                    "Pos": "pos",
                    subject_header: subject_key,
                    "Points": "points",
                    "Pts.": "points",
                    "Pts": "points",
                    "No.": "no",
                    "No": "no",
                },
                columns={
                    "pos": PositionColumn(),
                    subject_key: subject_column,
                    "points": PointsColumn(),
                    "no": IntColumn(),
                },
                default_column=RaceResultColumn(),
            )
            scraper = F1StandingsScraper(options=self._options, config=config)
            try:
                records = scraper.parse(soup)
                if records:
                    return records
            except RuntimeError:
                continue
        return []

    def _parse_table(
        self,
        soup: BeautifulSoup,
        *,
        section_ids: list[str],
        expected_headers: list[str],
        column_map: dict[str, str],
        columns: dict[str, Any],
        default_column: Any | None = None,
    ) -> List[Dict[str, Any]]:
        for section_id in section_ids:
            config = ScraperConfig(
                url=self.url,
                section_id=section_id,
                expected_headers=expected_headers,
                column_map=column_map,
                columns=columns,
                default_column=default_column,
            )
            pipeline = TablePipeline(
                config=config,
                include_urls=self.include_urls,
                skip_sentinel=self._SKIP,
            )
            parser = HtmlTableParser(
                section_id=pipeline.section_id,
                fragment=pipeline.fragment,
                expected_headers=pipeline.expected_headers,
                table_css_class=pipeline.table_css_class,
            )
            try:
                records: List[Dict[str, Any]] = []
                for row_index, row in enumerate(parser.parse(soup)):
                    record = pipeline.parse_cells(
                        row.headers,
                        row.cells,
                        row_index=row_index,
                    )
                    if record:
                        records.append(record)
                if records:
                    return records
            except RuntimeError:
                continue

        return []

    @staticmethod
    def _extract_year_from_url(url: str) -> int | None:
        match = re.search(r"/(\\d{4})_Formula_One", url)
        if match:
            return int(match.group(1))
        return None
