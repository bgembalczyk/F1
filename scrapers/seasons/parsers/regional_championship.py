from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types import DriverColumn
from scrapers.base.table.columns.types import TextColumn
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.columns.date import SeasonDateColumn
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonRegionalChampionshipParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self,
        soup: BeautifulSoup,
        *,
        section_ids: list[str],
        season_year: int | None,
    ) -> list[dict[str, Any]]:
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
            schema=TableSchemaDSL(
                columns=[
                    ColumnSpec("Race name", "race_name", TextColumn()),
                    ColumnSpec("Circuit", "circuit", UrlColumn()),
                    ColumnSpec("Date", "date", SeasonDateColumn(year=season_year)),
                    ColumnSpec("Winning driver", "winning_driver", DriverColumn()),
                    ColumnSpec("Constructor", "constructor", ConstructorColumn()),
                    ColumnSpec("Report", "report", UrlColumn()),
                ],
            ),
        )
