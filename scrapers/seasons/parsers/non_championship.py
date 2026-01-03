from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.season_date import SeasonDateColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonNonChampionshipParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self, soup: BeautifulSoup, season_year: int | None
    ) -> List[Dict[str, Any]]:
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
            column_map={
                "Race name": "race_name",
                "Circuit": "circuit",
                "Date": "date",
                "Winning driver": "winning_driver",
                "Constructor": "constructor",
                "Report": "report",
            },
            columns={
                "race_name": TextColumn(),
                "circuit": UrlColumn(),
                "date": SeasonDateColumn(year=season_year),
                "winning_driver": DriverColumn(),
                "constructor": ConstructorColumn(),
                "report": UrlColumn(),
            },
        )
