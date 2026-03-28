from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.records import record_from_mapping
from scrapers.seasons.columns.constructor import ConstructorColumn
from scrapers.base.table.columns.types import IntColumn
from scrapers.seasons.columns.points import PointsColumn
from scrapers.seasons.columns.position import PositionColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.columns.race_result import RaceResultColumn
from scrapers.base.table.columns.types import ConstructorColumn
from scrapers.seasons.parsers.standings import SeasonStandingsParser
from scrapers.seasons.parsers.table import SeasonTableParser


class ColinChapmanTrophyParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self,
        soup: BeautifulSoup,
        season_year: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Parses the Colin Chapman Trophy table.

        Table is identical to World Constructors' Championship standings,
        with one exception:
        - Mark * at race result means: "was not eligible for points, "
        "as the team had officially entered only one car for the "
        "entire championship"
        """

        records = self._table_parser.parse_standings_table(
            soup,
            section_ids=["Colin_Chapman_Trophy"],
            subject_header="Constructor",
            subject_key="constructor",
            subject_column=ConstructorColumn(),
            season_year=season_year,
            star_mark_note="single_car_entry_no_points",
        )
        # Apply the same merging logic as constructors standings
        return SeasonStandingsParser.merge_duplicate_constructors(records)
