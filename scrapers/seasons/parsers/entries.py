from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types import BrListColumn
from scrapers.base.table.columns.types import LinksListColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.columns.constructor import ConstructorColumn
from scrapers.seasons.columns.driver_list import DriverListColumn
from scrapers.seasons.columns.driver_rounds import DriversWithRoundsColumn
from scrapers.seasons.columns.engine import EngineColumn
from scrapers.seasons.columns.entrant import EntrantColumn
from scrapers.seasons.columns.tyre import TyreColumn
from scrapers.seasons.parsers.entry_merger import EntryMerger
from scrapers.seasons.parsers.table import SeasonTableParser
from scrapers.seasons.services.domain_parsing_policy import DomainParsingPolicy


class SeasonEntriesParser:
    def __init__(
        self,
        table_parser: SeasonTableParser,
        entry_merger: EntryMerger,
        policy: DomainParsingPolicy,
    ) -> None:
        self._table_parser = table_parser
        self._entry_merger = entry_merger
        self._policy = policy

    def parse(
        self,
        soup: BeautifulSoup,
        season_year: int | None,
    ) -> list[dict[str, Any]]:
        engine_config = self._policy.resolve_engine_config(season_year)
        engine_column = EngineColumn(global_config=engine_config)
        records = self._table_parser.parse_table(
            soup,
            section_ids=[
                "Entries",
                "Teams_and_drivers",
                "Drivers_and_constructors",
                "Championship_teams_and_drivers",
            ],
            expected_headers=["Entrant", "Constructor", "Chassis"],
            schema=TableSchemaDSL(
                columns=[
                    column("Entrant", "entrant", EntrantColumn()),
                    column("Constructor", "constructor", ConstructorColumn()),
                    column(
                        "Chassis",
                        "chassis",
                        LinksListColumn(text_for_missing_url=True),
                    ),
                    column("Power Unit", "power_unit", EngineColumn()),
                    column("Power unit", "power_unit", EngineColumn()),
                    column("Race drivers", "race_drivers", DriversWithRoundsColumn()),
                    column("Race drivers", "race_drivers", DriverListColumn()),
                    column("Race Drivers", "race_drivers", DriverListColumn()),
                    column("Race driver(s)", "race_drivers", DriversWithRoundsColumn()),
                    column("No.", "no", BrListColumn()),
                    column("Driver name", "drivers", DriverListColumn()),
                    column("Driver", "drivers", DriverListColumn()),
                    column("Rounds", "rounds", BrListColumn()),
                    column("Engine", "engine", engine_column),
                    column("Tyre", "tyre", TyreColumn()),
                ],
            ),
        )
        if self._policy.should_normalize_entry_numbers(season_year):
            records = self._normalize_pre_2007_entry_numbers(records)
        return self._entry_merger.merge_entries(records)

    @staticmethod
    def _normalize_pre_2007_entry_numbers(
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        for record in records:
            numbers = record.get("no")
            if numbers is None:
                continue

            numbers_list = numbers if isinstance(numbers, list) else [numbers]

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
