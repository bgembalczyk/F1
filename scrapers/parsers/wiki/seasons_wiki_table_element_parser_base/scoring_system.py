from typing import Any

from bs4 import BeautifulSoup

from scrapers.columns.factory import IntColumn
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.text import TextColumn
from scrapers.parsers.seasons_wiki_table_element_parser_base.base import BaseSeasonParser
from scrapers.parsers.seasons_wiki_table_element_parser_base.table import SeasonTableParser
from scrapers.table_schema_dsl import TableSchemaDSL


class SeasonScoringSystemParser(BaseSeasonParser):
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(self, soup: BeautifulSoup, season_year: int | None = None) -> list[dict[str, Any]]:
        return self._table_parser.parse_table(
            soup,
            section_ids=["Scoring_system", "Points_scoring_system"],
            expected_headers=["Position", "1st", "2nd", "3rd", "4th", "5th"],
            schema=TableSchemaDSL(
                columns=[ColumnSpec("Position", "position", TextColumn())],
            ),
            default_column=IntColumn(),
        )


__all__ = ["SeasonScoringSystemParser"]
