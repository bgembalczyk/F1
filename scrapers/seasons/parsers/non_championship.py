from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types import DriverColumn
from scrapers.base.table.columns.types import TextColumn
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.columns.date import SeasonDateColumn
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonNonChampionshipParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self,
        soup: BeautifulSoup,
        season_year: int | None,
    ) -> list[dict[str, Any]]:
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
            schema=TableSchemaDSL(
                columns=[
                    column("Race name", "race_name", TextColumn()),
                    column("Circuit", "circuit", UrlColumn()),
                    column("Date", "date", SeasonDateColumn(year=season_year)),
                    column("Winning driver", "winning_driver", DriverColumn()),
                    column("Constructor", "constructor", ConstructorColumn()),
                    column("Report", "report", UrlColumn()),
                ],
            ),
        )
