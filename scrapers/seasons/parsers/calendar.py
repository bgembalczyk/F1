from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.seasons.columns.calendar_circuit import CalendarCircuitColumn
from scrapers.seasons.columns.date import SeasonDateColumn
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonCalendarParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self, soup: BeautifulSoup, season_year: int | None
    ) -> List[Dict[str, Any]]:
        return self._table_parser.parse_table(
            soup,
            section_ids=["Calendar"],
            expected_headers=["Round", "Grand Prix", "Circuit", "Race date"],
            column_map={
                "Round": "round",
                "Grand Prix": "grand_prix",
                "Circuit": "circuit",
                "Race date": "race_date",
            },
            columns={
                "round": IntColumn(),
                "grand_prix": UrlColumn(),
                "circuit": CalendarCircuitColumn(),
                "race_date": SeasonDateColumn(year=season_year),
            },
        )
