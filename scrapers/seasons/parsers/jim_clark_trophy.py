from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.enum_marks import EnumMarksColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.points import PointsColumn
from scrapers.base.table.columns.types.position import PositionColumn
from scrapers.base.table.dsl import TableSchemaDSL, column
from scrapers.base.records import record_from_mapping
from scrapers.base.table.config import ScraperConfig
from scrapers.seasons.columns.race_result import RaceResultColumn
from scrapers.seasons.parsers.table import SeasonTableParser
from scrapers.seasons.standings_scraper import F1StandingsScraper


class JimClarkTrophyParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self, soup: BeautifulSoup, season_year: int | None = None
    ) -> List[Dict[str, Any]]:
        """
        Parsuje tabelę Jim Clark Trophy.
        
        Tabela jest identyczna jak World Drivers' Championship standings,
        z jednym wyjątkiem:
        - Mark * oznacza: "competed in insufficient events to be eligible for points"
        """
        
        # Tworzymy kolumnę dla kierowcy z obsługą marku *
        driver_with_mark = MultiColumn(
            columns={
                "driver": DriverColumn(),
                "insufficient_events_mark": EnumMarksColumn(
                    mapping={"*": True},
                    default=False
                ),
            }
        )
        
        schema_columns = [
            column("Pos.", "pos", PositionColumn()),
            column("Pos", "pos", PositionColumn()),
            column("Driver", "driver_data", driver_with_mark),
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
            default_column=RaceResultColumn(season_year=season_year),
            record_factory=record_from_mapping,
        )
        
        scraper = F1StandingsScraper(
            options=self._table_parser._options,
            config=config
        )
        
        try:
            records = scraper.parse(soup)
            # Przekształcamy driver_data na driver i dodajemy pole insufficient_events
            for record in records:
                if "driver_data" in record:
                    driver_data = record.pop("driver_data")
                    if isinstance(driver_data, dict):
                        record["driver"] = driver_data.get("driver")
                        if driver_data.get("insufficient_events_mark"):
                            record["insufficient_events"] = True
            return records
        except RuntimeError:
            return []
