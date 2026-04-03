from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.source_catalog import RED_FLAGGED_RACES
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.grands_prix.red_flagged_races_scraper.base import (
    RedFlaggedRacesBaseScraper,
)


class RedFlaggedWorldChampionshipRacesScraper(RedFlaggedRacesBaseScraper):
    alternative_section_ids = [
        "World_Championship_races",
        "Championship_races",
        "World_championship_races",
        "Red_flagged_races",
    ]

    schema_columns = RedFlaggedRacesBaseScraper.build_common_red_flag_columns()
    schema_columns[1] = column("Grand Prix", "grand_prix", UrlColumn())

    CONFIG = build_scraper_config(
        url=RED_FLAGGED_RACES.base_url,
        section_id=RED_FLAGGED_RACES.section_id,
        expected_headers=[
            "Year",
            "Grand Prix",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
        ],
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=RECORD_FACTORIES.mapping(),
    )
