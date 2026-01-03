from __future__ import annotations

import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from models.services.rounds_service import RoundsService
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.parsing import parse_int_from_text
from scrapers.base.options import ScraperOptions
from scrapers.base.scraper import F1Scraper
from scrapers.base.table.columns.types.calendar_circuit import CalendarCircuitColumn
from scrapers.base.table.columns.types.br_list import BrListColumn
from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.driver_rounds import DriversWithRoundsColumn
from scrapers.base.table.columns.types.entrant import EntrantColumn
from scrapers.base.table.columns.types.engine import EngineColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.season_date import SeasonDateColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.tyre import TyreColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.seasons.parsers.entry_merger import EntryMerger
from scrapers.seasons.parsers.season_table_parser import SeasonTableParser


class SingleSeasonScraper(F1Scraper):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        season_year: int | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        super().__init__(options=options)
        self.url: str = ""
        self.season_year = season_year
        self._options = options
        self._entry_merger = EntryMerger()
        self._table_parser = SeasonTableParser(
            options=self._options,
            include_urls=self.include_urls,
            url=self.url,
        )

    def fetch_by_url(
        self, url: str, *, season_year: int | None = None
    ) -> List[Dict[str, Any]]:
        self.url = url
        self._table_parser.update_url(url)
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
        records = self._parse_table(
            soup,
            section_ids=[
                "Entries",
                "Teams_and_drivers",
                "Drivers_and_constructors",
                "Championship_teams_and_drivers",
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
                "Driver name": "drivers",
                "Driver": "drivers",
                "Rounds": "rounds",
                "Engine": "engine",
                "Tyre": "tyre",
            },
            columns={
                "entrant": EntrantColumn(),
                "constructor": ConstructorColumn(),
                "chassis": LinksListColumn(text_for_missing_url=True),
                "power_unit": EngineColumn(),
                "race_drivers": DriversWithRoundsColumn(),
                "no": BrListColumn(),
                "drivers": DriverListColumn(),
                "rounds": BrListColumn(),
                "engine": EngineColumn(),
                "tyre": TyreColumn(),
            },
        )
        if self.season_year is not None and self.season_year < 2007:
            records = self._normalize_pre_2007_entry_numbers(records)
        return self._entry_merger.merge_entries(records)

    @staticmethod
    def _normalize_pre_2007_entry_numbers(
        records: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        for record in records:
            numbers = record.get("no")
            if numbers is None:
                continue

            if isinstance(numbers, list):
                numbers_list = numbers
            else:
                numbers_list = [numbers]

            if not numbers_list:
                continue

            drivers = record.get("race_drivers")
            if drivers is None:
                drivers = record.get("drivers") or record.get("driver")
            if not isinstance(drivers, list) or len(drivers) <= 1:
                continue

            primary_number = numbers_list[0]
            if isinstance(primary_number, str) and not primary_number.strip():
                continue

            if len(numbers_list) == 1 or all(
                isinstance(number, str) and not number.strip()
                for number in numbers_list[1:]
            ):
                record["no"] = [primary_number for _ in range(len(drivers))]

        return records

    def _parse_free_practice(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        records = self._parse_table(
            soup,
            section_ids=["Free_practice_drivers", "Friday_drivers"],
            expected_headers=["Constructor", "No.", "Driver name", "Rounds"],
            column_map={
                "Constructor": "constructor",
                "No.": "numbers",
                "No": "numbers",
                "Driver name": "drivers",
                "Driver": "drivers",
                "Rounds": "rounds",
            },
            columns={
                "constructor": ConstructorColumn(),
                "numbers": BrListColumn(),
                "drivers": DriverListColumn(),
                "rounds": BrListColumn(),
            },
        )
        records = self._filter_source_footer_records(records)
        if records:
            return self._normalize_free_practice_records(records)

        records = self._parse_table(
            soup,
            section_ids=["Free_practice_drivers"],
            expected_headers=["Constructor", "Driver name", "Rounds"],
            column_map={
                "Constructor": "constructor",
                "Driver name": "drivers",
                "Driver": "drivers",
                "Rounds": "rounds",
            },
            columns={
                "constructor": ConstructorColumn(),
                "drivers": DriverListColumn(),
                "rounds": BrListColumn(),
            },
        )
        records = self._filter_source_footer_records(records)
        if records:
            return self._normalize_free_practice_records(records)

        records = self._parse_table(
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
        return self._filter_source_footer_records(records)

    def _filter_source_footer_records(
        self, records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return [record for record in records if not self._is_source_footer_record(record)]

    def _is_source_footer_record(self, record: Dict[str, Any]) -> bool:
        texts: List[str] = []
        texts.extend(self._constructor_texts(record.get("constructor")))
        texts.extend(self._driver_list_texts(record.get("drivers")))
        texts.extend(self._practice_driver_texts(record.get("practice_drivers")))
        if not texts:
            return False
        return all(text == "Source:" for text in texts)

    def _constructor_texts(self, value: Any) -> List[str]:
        texts: List[str] = []
        if isinstance(value, list):
            for item in value:
                texts.extend(self._constructor_texts(item))
            return texts
        if isinstance(value, dict):
            for key in ("chassis_constructor", "engine_constructor"):
                text = self._get_text(value.get(key))
                if text:
                    texts.append(text)
            return texts
        text = self._get_text(value)
        return [text] if text else []

    def _driver_list_texts(self, value: Any) -> List[str]:
        if not isinstance(value, list):
            return []
        texts = []
        for item in value:
            text = self._get_text(item)
            if text:
                texts.append(text)
        return texts

    def _practice_driver_texts(self, value: Any) -> List[str]:
        if not isinstance(value, list):
            return []
        texts = []
        for item in value:
            if not isinstance(item, dict):
                continue
            text = self._get_text(item.get("driver"))
            if text:
                texts.append(text)
        return texts

    @staticmethod
    def _get_text(value: Any) -> str | None:
        if isinstance(value, dict):
            text = value.get("text")
            if isinstance(text, str):
                return text
        if isinstance(value, str):
            return value
        return None

    @staticmethod
    def _normalize_free_practice_records(
        records: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for record in records:
            drivers = record.pop("drivers", []) or []
            numbers = record.pop("numbers", []) or []
            rounds_list = record.pop("rounds", []) or []

            if len(numbers) == 1 and len(drivers) > 1:
                numbers = [numbers[0] for _ in range(len(drivers))]

            practice_drivers: List[Dict[str, Any]] = []
            for index, driver in enumerate(drivers):
                if not driver:
                    continue
                entry: Dict[str, Any] = {"driver": driver}

                if index < len(numbers):
                    number = parse_int_from_text(numbers[index])
                    if number is not None:
                        entry["no"] = number

                if index < len(rounds_list):
                    rounds_text = rounds_list[index]
                    rounds = RoundsService.parse_rounds(rounds_text)
                    if rounds_text or rounds:
                        entry["rounds"] = rounds

                practice_drivers.append(entry)

            record["practice_drivers"] = practice_drivers
            normalized.append(record)

        return normalized

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

    def _parse_constructors_standings(
        self, soup: BeautifulSoup
    ) -> List[Dict[str, Any]]:
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
        return self._table_parser.parse_standings_table(
            soup,
            section_ids=section_ids,
            subject_header=subject_header,
            subject_key=subject_key,
            subject_column=subject_column,
        )

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
        return self._table_parser.parse_table(
            soup,
            section_ids=section_ids,
            expected_headers=expected_headers,
            column_map=column_map,
            columns=columns,
            default_column=default_column,
        )

    @staticmethod
    def _extract_year_from_url(url: str) -> int | None:
        match = re.search(r"/(\\d{4})_Formula_One", url)
        if match:
            return int(match.group(1))
        return None
