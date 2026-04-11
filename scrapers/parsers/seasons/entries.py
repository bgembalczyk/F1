from typing import Any

from bs4 import BeautifulSoup

from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.br_list import BrListColumn
from scrapers.columns.types.constructor.constructor import ConstructorColumn
from scrapers.columns.types.driver_list import DriverListColumn
from scrapers.columns.types.driver_rounds import DriversWithRoundsColumn
from scrapers.columns.types.engine import EngineColumn
from scrapers.columns.types.entrant import EntrantColumn
from scrapers.columns.types.links_list import LinksListColumn
from scrapers.columns.types.tyre import TyreColumn
from scrapers.domain_parsing_policy import DomainParsingPolicy
from scrapers.parsers.seasons.entry_merger import EntryMerger
from scrapers.parsers.seasons.table import SeasonTableService
from scrapers.table_schema_dsl import TableSchemaDSL
from scrapers.parsers.seasons.base import BaseSeasonParser


class SeasonEntriesParser(BaseSeasonParser):
    def __init__(
        self,
        table_parser: SeasonTableService,
        entry_merger: EntryMerger,
        policy: DomainParsingPolicy,
    ) -> None:
        self._table_parser = table_parser
        self._entry_merger = entry_merger
        self._policy = policy

    def parse(
        self,
        soup: BeautifulSoup,
        season_year: int | None = None,
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
                    ColumnSpec("Entrant", "entrant", EntrantColumn()),
                    ColumnSpec("Constructor", "constructor", ConstructorColumn()),
                    ColumnSpec(
                        "Chassis",
                        "chassis",
                        LinksListColumn(text_for_missing_url=True),
                    ),
                    ColumnSpec("Power Unit", "power_unit", EngineColumn()),
                    ColumnSpec("Power unit", "power_unit", EngineColumn()),
                    ColumnSpec(
                        "Race drivers",
                        "race_drivers",
                        DriversWithRoundsColumn(),
                    ),
                    ColumnSpec("Race drivers", "race_drivers", DriverListColumn()),
                    ColumnSpec("Race Drivers", "race_drivers", DriverListColumn()),
                    ColumnSpec(
                        "Race driver(s)",
                        "race_drivers",
                        DriversWithRoundsColumn(),
                    ),
                    ColumnSpec("No.", "no", BrListColumn()),
                    ColumnSpec("Driver name", "drivers", DriverListColumn()),
                    ColumnSpec("Driver", "drivers", DriverListColumn()),
                    ColumnSpec("Rounds", "rounds", BrListColumn()),
                    ColumnSpec("Engine", "engine", engine_column),
                    ColumnSpec("Tyre", "tyre", TyreColumn()),
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


__all__ = ["SeasonEntriesParser"]
