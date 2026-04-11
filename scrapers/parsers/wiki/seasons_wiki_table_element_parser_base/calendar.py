from typing import Any

from bs4 import BeautifulSoup

from scrapers.columns.factory import IntColumn
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.calendar_circuit import CalendarCircuitColumn
from scrapers.columns.types.season_date import SeasonDateColumn
from scrapers.columns.types.url import UrlColumn
from scrapers.parsers.seasons_wiki_table_element_parser_base.table import SeasonTableParser
from scrapers.table_schema_dsl import TableSchemaDSL
from scrapers.parsers.seasons_wiki_table_element_parser_base.base import BaseSeasonParser


class SeasonCalendarParser(BaseSeasonParser):
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self,
        soup: BeautifulSoup,
        season_year: int | None = None,
    ) -> list[dict[str, Any]]:
        schema_columns = [
            ColumnSpec("Round", "round", IntColumn()),
            ColumnSpec("Grand Prix", "grand_prix", UrlColumn()),
            ColumnSpec("Circuit", "circuit", CalendarCircuitColumn()),
            ColumnSpec("Race date", "race_date", SeasonDateColumn(year=season_year)),
            ColumnSpec("Date", "race_date", SeasonDateColumn(year=season_year)),
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


__all__ = ["SeasonCalendarParser"]
