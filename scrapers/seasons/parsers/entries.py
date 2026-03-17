from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.br_list import BrListColumn
from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.engine import EngineColumn
from scrapers.base.table.columns.types.entrant import EntrantColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.tyre import TyreColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.columns.driver_rounds import DriversWithRoundsColumn
from scrapers.seasons.parsers.constants import ENGINE_V10_END_YEAR
from scrapers.seasons.parsers.constants import ENGINE_V10_START_YEAR
from scrapers.seasons.parsers.constants import ENGINE_V8_YEAR
from scrapers.seasons.parsers.constants import PRE_2007_NORMALIZATION_CUTOFF
from scrapers.seasons.parsers.entry_merger import EntryMerger
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonEntriesParser:
    def __init__(
        self,
        table_parser: SeasonTableParser,
        entry_merger: EntryMerger,
    ) -> None:
        self._table_parser = table_parser
        self._entry_merger = entry_merger

    def parse(
        self,
        soup: BeautifulSoup,
        season_year: int | None,
    ) -> list[dict[str, Any]]:
        engine_config = self._global_engine_config(season_year)
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
        if season_year is not None and season_year < PRE_2007_NORMALIZATION_CUTOFF:
            records = self._normalize_pre_2007_entry_numbers(records)
        return self._entry_merger.merge_entries(records)

    @staticmethod
    def _global_engine_config(
        season_year: int | None,
    ) -> dict[str, Any] | None:
        if season_year == ENGINE_V8_YEAR:
            return {"displacement_l": 2.4, "layout": "V", "cylinders": 8}
        if (
            season_year is not None
            and ENGINE_V10_START_YEAR <= season_year <= ENGINE_V10_END_YEAR
        ):
            return {"displacement_l": 3.0, "layout": "V", "cylinders": 10}
        return None

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
