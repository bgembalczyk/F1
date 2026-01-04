from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.dsl import TableSchemaDSL, column
from scrapers.seasons.columns.calendar_circuit import CalendarCircuitColumn
from scrapers.seasons.columns.date import SeasonDateColumn
from scrapers.seasons.parsers.table import SeasonTableParser


class CancelledRoundsParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self, soup: BeautifulSoup, season_year: int | None
    ) -> List[Dict[str, Any]]:
        schema_columns = [
            column("Grand Prix", "grand_prix", UrlColumn()),
            column("Circuit", "circuit", CalendarCircuitColumn()),
            column("Scheduled date", "scheduled_date", SeasonDateColumn(year=season_year)),
            column("Original date", "scheduled_date", SeasonDateColumn(year=season_year)),
            column("Date", "scheduled_date", SeasonDateColumn(year=season_year)),
        ]
        schema = TableSchemaDSL(columns=schema_columns)
        
        # Try different sections in order
        section_ids = [
            "Cancelled_Grands_Prix",
            "Provisional_calendar", 
            "Calendar"
        ]
        
        for section_id in section_ids:
            records = self._table_parser.parse_table(
                soup,
                section_ids=[section_id],
                expected_headers=["Grand Prix", "Circuit"],
                schema=schema,
            )
            if records:
                return records
        
        return []
