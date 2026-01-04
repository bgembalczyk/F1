from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.time_range import TimeRangeColumn
from scrapers.base.table.dsl import TableSchemaDSL, column
from scrapers.seasons.columns.calendar_circuit import CalendarCircuitColumn
from scrapers.seasons.columns.date import SeasonDateColumn
from scrapers.seasons.columns.date_range import DateRangeColumn
from scrapers.seasons.parsers.table import SeasonTableParser


class TestingVenuesParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self, soup: BeautifulSoup, season_year: int | None
    ) -> List[Dict[str, Any]]:
        # This table only exists in 2011 and 2009
        if season_year not in {2009, 2011}:
            return []

        if season_year == 2011:
            return self._parse_2011(soup, season_year)
        else:  # 2009
            return self._parse_2009(soup, season_year)

    def _parse_2011(
        self, soup: BeautifulSoup, season_year: int | None
    ) -> List[Dict[str, Any]]:
        """
        Parses the testing table for 2011.
        
        Note: Circuit and Event have swapped content in the source data!
        - Circuit contains text that should be in Event
        - Event contains circuit data that should be in Circuit
        
        We parse them as-is and then swap them to correct the Wikipedia error.
        """
        schema_columns = [
            column("Test", "test", IntColumn()),
            # Swapped content - Circuit contains text
            column("Circuit", "circuit", TextColumn()),
            # Swapped content - Event contains circuit data
            column("Event", "event", CalendarCircuitColumn()),
            # Session Timings has subcolumns Morning and Afternoon
            column("Morning", "session_timings_morning", TimeRangeColumn()),
            column("Afternoon", "session_timings_afternoon", TimeRangeColumn()),
            # Dates has subcolumns Start and End
            column("Start", "dates_start", SeasonDateColumn(year=season_year)),
            column("End", "dates_end", SeasonDateColumn(year=season_year)),
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
        self, soup: BeautifulSoup, season_year: int | None
    ) -> List[Dict[str, Any]]:
        """
        Parses the testing table for 2009.
        """
        schema_columns = [
            column("Test", "test", IntColumn()),
            column("Event", "event", TextColumn()),
            column("Circuit", "circuit", CalendarCircuitColumn()),
            column("Dates", "dates", DateRangeColumn(year=season_year)),
        ]
        schema = TableSchemaDSL(columns=schema_columns)
        
        return self._table_parser.parse_table(
            soup,
            section_ids=["Testing_venues_and_dates"],
            expected_headers=["Test", "Event", "Circuit", "Dates"],
            schema=schema,
        )
