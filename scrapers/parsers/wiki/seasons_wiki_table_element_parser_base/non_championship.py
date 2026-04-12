from typing import Any

from bs4 import BeautifulSoup

from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.constructor.constructor import ConstructorColumn
from scrapers.columns.types.driver import DriverColumn
from scrapers.columns.types.season_date import SeasonDateColumn
from scrapers.columns.types.text import TextColumn
from scrapers.columns.types.url import UrlColumn
from scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.base import BaseSeasonParser
from scrapers.orchestration.season_table_parsing_service import SeasonTableParsingService
from scrapers.table_schema_dsl import TableSchemaDSL


class SeasonNonChampionshipParser(BaseSeasonParser):
    def __init__(self, table_parser: SeasonTableParsingService) -> None:
        self._table_parser = table_parser

    def parse(
        self,
        soup: BeautifulSoup,
        season_year: int | None = None,
    ) -> list[dict[str, Any]]:
        return self._table_parser.parse(
            soup,
            mode="table",
            section_ids=["Non-championship_races", "Non-championship_race"],
            expected_headers=[
                "Race name",
                "Circuit",
                "Date",
                "Winning driver",
                "Constructor",
                "Report",
            ],
            schema=TableSchemaDSL(
                columns=[
                    ColumnSpec("Race name", "race_name", TextColumn()),
                    ColumnSpec("Circuit", "circuit", UrlColumn()),
                    ColumnSpec("Date", "date", SeasonDateColumn(year=season_year)),
                    ColumnSpec("Winning driver", "winning_driver", DriverColumn()),
                    ColumnSpec("Constructor", "constructor", ConstructorColumn()),
                    ColumnSpec("Report", "report", UrlColumn()),
                ],
            ),
        )


__all__ = ["SeasonNonChampionshipParser"]
