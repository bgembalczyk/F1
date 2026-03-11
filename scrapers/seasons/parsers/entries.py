from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.br_list import BrListColumn
from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.engine import EngineColumn
from scrapers.base.table.columns.types.entrant import EntrantColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.tyre import TyreColumn
from scrapers.base.table.dsl import TableSchemaDSL
from scrapers.base.table.dsl import column
from scrapers.seasons.columns.driver_rounds import DriversWithRoundsColumn
from scrapers.seasons.parsers.entry_merger import EntryMerger
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonEntriesParser:
    def __init__(
            self, table_parser: SeasonTableParser, entry_merger: EntryMerger,
    ) -> None:
        self._table_parser = table_parser
        self._entry_merger = entry_merger

    def parse(
            self, soup: BeautifulSoup, season_year: int | None,
    ) -> List[Dict[str, Any]]:
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
        if season_year is not None and season_year < 2007:
            records = self._normalize_pre_2007_entry_numbers(records)
        return self._entry_merger.merge_entries(records)

    @staticmethod
    def _global_engine_config(
            season_year: int | None,
    ) -> dict[str, Any] | None:
        if season_year == 2008:
            return {"displacement_l": 2.4, "layout": "V", "cylinders": 8}
        if season_year is not None and 1998 <= season_year <= 2005:
            return {"displacement_l": 3.0, "layout": "V", "cylinders": 10}
        return None

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
                    for number in numbers_list[1:],
            ):
                record["no"] = [primary_number for _ in range(len(drivers))]

        return records
