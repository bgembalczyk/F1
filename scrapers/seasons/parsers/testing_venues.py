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
        # Ta tabela występuje tylko w 2011 i 2009
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
        Parsuje tabelę testów dla roku 2011.
        
        Uwaga: Circuit i Event mają zamienioną zawartość w źródłowych danych!
        - Circuit zawiera tekst który powinien być w Event
        - Event zawiera dane obwodu który powinien być w Circuit
        """
        schema_columns = [
            column("Test", "test", IntColumn()),
            # Zamieniona zawartość - Circuit zawiera tekst
            column("Circuit", "circuit", TextColumn()),
            # Zamieniona zawartość - Event zawiera dane obwodu
            column("Event", "event", CalendarCircuitColumn()),
            # Session Timings ma podkolumny Morning i Afternoon
            column("Morning", "session_timings_morning", TimeRangeColumn()),
            column("Afternoon", "session_timings_afternoon", TimeRangeColumn()),
            # Dates ma podkolumny Start i End
            column("Start", "dates_start", SeasonDateColumn(year=season_year)),
            column("End", "dates_end", SeasonDateColumn(year=season_year)),
        ]
        schema = TableSchemaDSL(columns=schema_columns)
        
        return self._table_parser.parse_table(
            soup,
            section_ids=["Testing_venues_and_dates"],
            expected_headers=["Test", "Circuit", "Event"],
            schema=schema,
        )

    def _parse_2009(
        self, soup: BeautifulSoup, season_year: int | None
    ) -> List[Dict[str, Any]]:
        """
        Parsuje tabelę testów dla roku 2009.
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
