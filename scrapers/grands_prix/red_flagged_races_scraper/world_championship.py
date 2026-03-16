from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.records import record_from_mapping
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.grands_prix.columns.restart_status import RestartStatusColumn
from scrapers.grands_prix.red_flagged_races_scraper.base import (
    RedFlaggedRacesBaseScraper,
)
from scrapers.wiki.parsers.section_alias_registry import get_aliases


class RedFlaggedWorldChampionshipRacesScraper(RedFlaggedRacesBaseScraper):
    alternative_section_ids = get_aliases("grands_prix", "Red-flagged_races")


    schema_columns = [
        column("Year", "season", IntColumn()),
        column("Grand Prix", "grand_prix", UrlColumn()),
        column("Lap", "lap", IntColumn()),
        column("R", "restart_status", RestartStatusColumn()),
        column("Winner", "winner", DriverColumn()),
        column("Incident that prompted red flag", "incident", TextColumn()),
        column(
            "Failed to make the restart - Drivers",
            "failed_to_make_restart_drivers",
            DriverListColumn(),
        ),
        column(
            "Failed to make the restart - Reason",
            "failed_to_make_restart_reason",
            TextColumn(),
        ),
        column("Ref.", "ref", SkipColumn()),
    ]

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_red-flagged_Formula_One_races",
        section_id="Red-flagged_races",
        expected_headers=[
            "Year",
            "Grand Prix",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
        ],
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=record_from_mapping,
    )


if __name__ == "__main__":
    run_and_export(
        RedFlaggedWorldChampionshipRacesScraper,
        "grands_prix/f1_red_flagged_world_championship_races.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
