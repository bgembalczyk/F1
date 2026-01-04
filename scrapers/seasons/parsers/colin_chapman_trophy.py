from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.points import PointsColumn
from scrapers.base.table.columns.types.position import PositionColumn
from scrapers.base.table.dsl import TableSchemaDSL, column
from scrapers.base.records import record_from_mapping
from scrapers.base.table.config import ScraperConfig
from scrapers.seasons.columns.colin_chapman_race_result import ColinChapmanRaceResultColumn
from scrapers.seasons.parsers.table import SeasonTableParser
from scrapers.seasons.parsers.standings import SeasonStandingsParser
from scrapers.seasons.standings_scraper import F1StandingsScraper


class ColinChapmanTrophyParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self, soup: BeautifulSoup, season_year: int | None = None
    ) -> List[Dict[str, Any]]:
        """
        Parses the Colin Chapman Trophy table.
        
        Table is identical to World Constructors' Championship standings,
        with one exception:
        - Mark * at race result means: "was not eligible for points, as the team had officially entered only one car for the entire championship"
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
            default_column=ColinChapmanRaceResultColumn(season_year=season_year),
            record_factory=record_from_mapping,
        )
        
        scraper = F1StandingsScraper(
            options=self._table_parser._options,
            config=config
        )
        
        try:
            records = scraper.parse(soup)
            # Apply the same merging logic as constructors standings
            return SeasonStandingsParser.merge_duplicate_constructors(records)
        except RuntimeError:
            return []
