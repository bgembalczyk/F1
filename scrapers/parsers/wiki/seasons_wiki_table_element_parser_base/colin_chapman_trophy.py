from typing import Any

from bs4 import BeautifulSoup

from scrapers.columns.types.constructor.constructor import ConstructorColumn
from scrapers.orchestration.season_table_parsing_service import (
    SeasonTableParsingService,
)
from scrapers.parsers.wiki.season_standings import SeasonStandingsParser
from scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.base import (
    BaseSeasonParser,
)


class ColinChapmanTrophyParser(BaseSeasonParser):
    def __init__(self, table_parser: SeasonTableParsingService) -> None:
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

        records = self._table_parser.standings_orchestrator.parse(
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


__all__ = ["ColinChapmanTrophyParser"]
