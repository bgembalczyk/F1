from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonScoringSystemParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._table_parser.parse_table(
            soup,
            section_ids=["Scoring_system", "Points_scoring_system"],
            expected_headers=["Position", "1st", "2nd", "3rd", "4th", "5th"],
            column_map={
                "Position": "position",
            },
            columns={
                "position": TextColumn(),
            },
            default_column=IntColumn(),
        )
