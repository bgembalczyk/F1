from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.constructor import ConstructorColumn
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


class ColinChapmanTrophyParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self, soup: BeautifulSoup, season_year: int | None = None
    ) -> List[Dict[str, Any]]:
        """
        Parsuje tabelę Colin Chapman Trophy.
        
        Tabela jest identyczna jak World Constructors' Championship standings,
        z jednym wyjątkiem:
        - Mark * oznacza: "was not eligible for points, as the team had officially entered only one car for the entire championship"
        """
        
        # Tworzymy kolumnę dla konstruktora z obsługą marku *
        constructor_with_mark = MultiColumn(
            subcolumns={
                "constructor": ConstructorColumn(),
                "single_car_entry_mark": EnumMarksColumn(
                    mapping={"*": True},
                    default=False
                ),
            }
        )
        
        schema_columns = [
            column("Pos.", "pos", PositionColumn()),
            column("Pos", "pos", PositionColumn()),
            column("Constructor", "constructor_data", constructor_with_mark),
            column("Points", "points", PointsColumn()),
            column("Pts.", "points", PointsColumn()),
            column("Pts", "points", PointsColumn()),
            column("No.", "no", IntColumn()),
            column("No", "no", IntColumn()),
        ]
        
        config = ScraperConfig(
            url=self._table_parser.url,
            section_id="Colin_Chapman_Trophy",
            expected_headers=["Constructor"],
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
            # Przekształcamy constructor_data na constructor i dodajemy pole single_car_entry
            for record in records:
                if "constructor_data" in record:
                    constructor_data = record.pop("constructor_data")
                    if isinstance(constructor_data, dict):
                        record["constructor"] = constructor_data.get("constructor")
                        if constructor_data.get("single_car_entry_mark"):
                            record["single_car_entry"] = True
            return records
        except RuntimeError:
            return []
