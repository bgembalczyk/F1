from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.table.columns.types import ConstructorColumn
from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import PointsColumn
from scrapers.base.table.columns.types import PositionColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.columns.race_result import RaceResultColumn
from scrapers.seasons.parsers.standings import SeasonStandingsParser
from scrapers.seasons.parsers.table import SeasonTableParser
from scrapers.seasons.standings_scraper import F1StandingsScraper


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

        schema_columns = [
            column("Pos.", "pos", PositionColumn()),
            column("Pos", "pos", PositionColumn()),
            column("Constructor", "constructor", ConstructorColumn()),
            column("Points", "points", PointsColumn()),
            column("Pts.", "points", PointsColumn()),
            column("Pts", "points", PointsColumn()),
            column("No.", "no", IntColumn()),
            column("No", "no", IntColumn()),
            # Handle "Car<br>no." which becomes "Car no." after text extraction
            column("Car no.", "no", IntColumn()),
        ]

        config = ScraperConfig(
            url=self._table_parser.url,
            section_id="Colin_Chapman_Trophy",
            expected_headers=["Constructor"],
            schema=TableSchemaDSL(columns=schema_columns),
            default_column=RaceResultColumn(
                season_year=season_year,
                star_mark_note="single_car_entry_no_points",
            ),
            record_factory=RECORD_FACTORIES.mapping(),
        )

        scraper = F1StandingsScraper(options=self._table_parser.options, config=config)

        try:
            records = scraper.parse(soup)
            # Apply the same merging logic as constructors standings
            return SeasonStandingsParser.merge_duplicate_constructors(records)
        except RuntimeError:
            return []
