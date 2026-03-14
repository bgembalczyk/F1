from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.tyre import TyreColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonResultsParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self._table_parser.parse_table(
            soup,
            section_ids=["Grands_Prix", "Results_and_standings"],
            expected_headers=[
                "Round",
                "Fastest lap",
                "Winning driver",
                "Report",
            ],
            schema=TableSchemaDSL(
                columns=[
                    column("Round", "round", IntColumn()),
                    column("Grand Prix", "grand_prix", UrlColumn()),
                    column("Race", "grand_prix", UrlColumn()),
                    column("Pole position", "pole_position", DriverColumn()),
                    column("Pole Position", "pole_position", DriverColumn()),
                    column("Fastest lap", "fastest_lap", DriverListColumn()),
                    column("Winning driver", "winning_driver", DriverColumn()),
                    column(
                        "Winning constructor",
                        "winning_constructor",
                        ConstructorColumn(),
                    ),
                    column("Constructor", "winning_constructor", ConstructorColumn()),
                    column("Report", "report", UrlColumn()),
                    column("Tyre", "tyre", TyreColumn()),
                ],
            ),
        )
