from scrapers.base.factory.record_factory import MappingRecordFactory
from scrapers.base.source_catalog import RED_FLAGGED_RACES
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.races.red_flagged_races_scraper.base import (
    RedFlaggedRacesBaseScraper,
)


class RedFlaggedNonChampionshipRacesScraper(RedFlaggedRacesBaseScraper):
    alternative_section_ids = [
        "Non-championship",
        "Non-Championship_races",
        "Non_championship_races",
    ]

    schema_columns = RedFlaggedRacesBaseScraper.build_common_red_flag_columns(
        "Event",
    )
    schema_columns[1] = ColumnSpec("Event", "event", UrlColumn())

    CONFIG = build_scraper_config(
        url=RED_FLAGGED_RACES.base_url,
        section_id="Non-championship_races",
        expected_headers=[
            "Year",
            "Event",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
        ],
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=MappingRecordFactory(),
    )
