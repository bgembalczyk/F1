from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonStandingsParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse_drivers(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._parse_standings_table(
            soup,
            section_ids=[
                "World_Drivers'_Championship_standings",
                "World_Championship_of_Drivers_standings",
            ],
            subject_header="Driver",
            subject_key="driver",
            subject_column=DriverColumn(),
        )

    def parse_constructors(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._parse_standings_table(
            soup,
            section_ids=[
                "World_Constructors'_Championship_standings",
                "International_Cup_for_F1_Constructors_standings",
            ],
            subject_header="Constructor",
            subject_key="constructor",
            subject_column=ConstructorColumn(),
        )

    def _parse_standings_table(
        self,
        soup: BeautifulSoup,
        *,
        section_ids: list[str],
        subject_header: str,
        subject_key: str,
        subject_column: Any,
    ) -> List[Dict[str, Any]]:
        return self._table_parser.parse_standings_table(
            soup,
            section_ids=section_ids,
            subject_header=subject_header,
            subject_key=subject_key,
            subject_column=subject_column,
        )
