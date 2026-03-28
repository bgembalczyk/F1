from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.records import record_from_mapping
from scrapers.seasons.columns.driver import DriverColumn
from scrapers.base.table.columns.types import IntColumn
from scrapers.seasons.columns.points import PointsColumn
from scrapers.seasons.columns.position import PositionColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.columns.race_result import RaceResultColumn
from scrapers.base.table.columns.types import DriverColumn
from scrapers.seasons.parsers.table import SeasonTableParser


class JimClarkTrophyParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self,
        soup: BeautifulSoup,
        season_year: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Parses the Jim Clark Trophy table.

        Table is identical to World Drivers' Championship standings,
        with one exception:
        - Mark * at race result means: "competed in insufficient events "
        "to be eligible for points"
        """

        return self._table_parser.parse_standings_table(
            soup,
            section_ids=["Jim_Clark_Trophy"],
            subject_header="Driver",
            subject_key="driver",
            subject_column=DriverColumn(),
            season_year=season_year,
            star_mark_note="insufficient_events_to_be_eligible",
            include_car_no_column=False,
        )
