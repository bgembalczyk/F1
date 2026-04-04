from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import TextColumn
from scrapers.base.table.columns.types import TimeRangeColumn
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.columns.calendar_circuit import CalendarCircuitColumn
from scrapers.seasons.columns.date import SeasonDateColumn
from scrapers.seasons.columns.date_range import DateRangeColumn
from scrapers.seasons.parsers.table import SeasonTableParser
from scrapers.seasons.services.domain_parsing_policy import DomainParsingPolicy
from scrapers.seasons.services.domain_parsing_policy import TestingVenuesLayout


class TestingVenuesParser:
    def __init__(
        self,
        table_parser: SeasonTableParser,
        policy: DomainParsingPolicy,
    ) -> None:
        self._table_parser = table_parser
        self._policy = policy

    def parse(
        self,
        soup: BeautifulSoup,
        season_year: int | None,
    ) -> list[dict[str, Any]]:
        layout = self._policy.resolve_testing_venues_layout(season_year)
        if layout is None:
            return []
        if layout is TestingVenuesLayout.SWAPPED_CIRCUIT_EVENT:
            return self._parse_2011(soup, season_year)
        return self._parse_2009(soup, season_year)

    def _parse_2011(
        self,
        soup: BeautifulSoup,
        season_year: int | None,
    ) -> list[dict[str, Any]]:
        """
        Parses the testing table for 2011.

        Note: Circuit and Event have swapped content in the source data!
        - Circuit contains text that should be in Event
        - Event contains circuit data that should be in Circuit

        We parse them as-is and then swap them to correct the Wikipedia error.
        """
        schema_columns = [
            ColumnSpec("Test", "test", IntColumn()),
            # Swapped content - Circuit contains text
            ColumnSpec("Circuit", "circuit", TextColumn()),
            # Swapped content - Event contains circuit data
            ColumnSpec("Event", "event", CalendarCircuitColumn()),
            # Session Timings has subcolumns Morning and Afternoon
            ColumnSpec("Morning", "session_timings_morning", TimeRangeColumn()),
            ColumnSpec("Afternoon", "session_timings_afternoon", TimeRangeColumn()),
            # Dates has subcolumns Start and End
            ColumnSpec("Start", "dates_start", SeasonDateColumn(year=season_year)),
            ColumnSpec("End", "dates_end", SeasonDateColumn(year=season_year)),
        ]
        schema = TableSchemaDSL(columns=schema_columns)

        records = self._table_parser.parse_table(
            soup,
            section_ids=["Testing_venues_and_dates"],
            expected_headers=["Test", "Circuit", "Event"],
            schema=schema,
        )

        # Swap circuit and event fields to correct the Wikipedia error
        for record in records:
            if "circuit" in record and "event" in record:
                record["circuit"], record["event"] = record["event"], record["circuit"]

        return records

    def _parse_2009(
        self,
        soup: BeautifulSoup,
        season_year: int | None,
    ) -> list[dict[str, Any]]:
        """
        Parses the testing table for 2009.
        """
        schema_columns = [
            ColumnSpec("Test", "test", IntColumn()),
            ColumnSpec("Event", "event", TextColumn()),
            ColumnSpec("Circuit", "circuit", CalendarCircuitColumn()),
            ColumnSpec("Dates", "dates", DateRangeColumn(year=season_year)),
        ]
        schema = TableSchemaDSL(columns=schema_columns)

        return self._table_parser.parse_table(
            soup,
            section_ids=["Testing_venues_and_dates"],
            expected_headers=["Test", "Event", "Circuit", "Dates"],
            schema=schema,
        )
