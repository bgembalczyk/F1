from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.parsers.table import SeasonTableParser
from scrapers.wiki.parsers.section_alias_registry import get_aliases


class SeasonScoringSystemParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self._table_parser.parse_table(
            soup,
            section_ids=["Scoring_system", *get_aliases("seasons", "Scoring_system")],
            expected_headers=["Position", "1st", "2nd", "3rd", "4th", "5th"],
            schema=TableSchemaDSL(
                columns=[column("Position", "position", TextColumn())],
            ),
            default_column=IntColumn(),
        )
