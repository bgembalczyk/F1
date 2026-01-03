from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.tyre import TyreColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonResultsParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._table_parser.parse_table(
            soup,
            section_ids=["Grands_Prix", "Results_and_standings"],
            expected_headers=[
                "Round",
                "Fastest lap",
                "Winning driver",
                "Report",
            ],
            column_map={
                "Round": "round",
                "Grand Prix": "grand_prix",
                "Race": "grand_prix",
                "Pole position": "pole_position",
                "Pole Position": "pole_position",
                "Fastest lap": "fastest_lap",
                "Winning driver": "winning_driver",
                "Winning constructor": "winning_constructor",
                "Constructor": "winning_constructor",
                "Report": "report",
                "Tyre": "tyre",
            },
            columns={
                "round": IntColumn(),
                "grand_prix": UrlColumn(),
                "pole_position": DriverColumn(),
                "fastest_lap": DriverListColumn(),
                "winning_driver": DriverColumn(),
                "winning_constructor": ConstructorColumn(),
                "report": UrlColumn(),
                "tyre": TyreColumn(),
            },
        )
