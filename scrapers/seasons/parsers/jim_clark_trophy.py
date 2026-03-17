from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.records import record_from_mapping
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.points import PointsColumn
from scrapers.base.table.columns.types.position import PositionColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.columns.race_result import RaceResultColumn
from scrapers.seasons.parsers.table import SeasonTableParser
from scrapers.seasons.standings_scraper import F1StandingsScraper


class JimClarkTrophyParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self,
        soup: BeautifulSoup,
        season_year: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Parses the Jim Clark Trophy table.

        Table is identical to World Drivers' Championship standings,
        with one exception:
        - Mark * at race result means: "competed in insufficient events "
        "to be eligible for points"
        """

        schema_columns = [
            column("Pos.", "pos", PositionColumn()),
            column("Pos", "pos", PositionColumn()),
            column("Driver", "driver", DriverColumn()),
            column("Points", "points", PointsColumn()),
            column("Pts.", "points", PointsColumn()),
            column("Pts", "points", PointsColumn()),
            column("No.", "no", IntColumn()),
            column("No", "no", IntColumn()),
        ]

        config = ScraperConfig(
            url=self._table_parser.url,
            section_id="Jim_Clark_Trophy",
            expected_headers=["Driver"],
            schema=TableSchemaDSL(columns=schema_columns),
            default_column=RaceResultColumn(
                season_year=season_year,
                star_mark_note="insufficient_events_to_be_eligible",
            ),
            record_factory=record_from_mapping,
        )

        scraper = F1StandingsScraper(options=self._table_parser.options, config=config)

        try:
            return scraper.parse(soup)
        except RuntimeError:
            return []
