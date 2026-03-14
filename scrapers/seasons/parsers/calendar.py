from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.dsl import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.columns.calendar_circuit import CalendarCircuitColumn
from scrapers.seasons.columns.date import SeasonDateColumn
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonCalendarParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self,
        soup: BeautifulSoup,
        season_year: int | None,
    ) -> list[dict[str, Any]]:
        schema_columns = [
            column("Round", "round", IntColumn()),
            column("Grand Prix", "grand_prix", UrlColumn()),
            column("Circuit", "circuit", CalendarCircuitColumn()),
            column("Race date", "race_date", SeasonDateColumn(year=season_year)),
            column("Date", "race_date", SeasonDateColumn(year=season_year)),
        ]
        schema = TableSchemaDSL(columns=schema_columns)
        records = self._table_parser.parse_table(
            soup,
            section_ids=["Calendar"],
            expected_headers=["Round", "Grand Prix", "Circuit", "Race date"],
            schema=schema,
        )
        if records:
            return records

        return self._table_parser.parse_table(
            soup,
            section_ids=["Calendar"],
            expected_headers=["Round", "Grand Prix", "Circuit", "Date"],
            schema=schema,
        )
