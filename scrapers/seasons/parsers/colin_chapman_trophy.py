from typing import Any

from bs4 import BeautifulSoup

from scrapers.constructors.columns.constructor import ConstructorColumn
from scrapers.seasons.parsers.standings import SeasonStandingsParser
from scrapers.seasons.parsers.table import SeasonTableParser


class ColinChapmanTrophyParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self,
        soup: BeautifulSoup,
        season_year: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Parses the Colin Chapman Trophy table.

        Table is identical to World Constructors' Championship standings,
        with one exception:
        - Mark * at race result means: "was not eligible for points, "
        "as the team had officially entered only one car for the "
        "entire championship"
        """

        records = self._table_parser.parse_standings_table(
            soup,
            section_ids=["Colin_Chapman_Trophy"],
            subject_header="Constructor",
            subject_key="constructor",
            subject_column=ConstructorColumn(),
            season_year=season_year,
            star_mark_note="single_car_entry_no_points",
        )
        # Apply the same merging logic as constructors standings
        return SeasonStandingsParser.merge_duplicate_constructors(records)
