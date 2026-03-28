from scrapers.base.records import record_from_mapping
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import TableScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.grands_prix.columns.restart_status import RestartStatusColumn
from scrapers.grands_prix.red_flagged_races_scraper.base import (
    RedFlaggedRacesBaseScraper,
)


class RedFlaggedNonChampionshipRacesScraper(RedFlaggedRacesBaseScraper):
    alternative_section_ids = [
        "Non-championship",
        "Non-Championship_races",
        "Non_championship_races",
    ]

    schema_columns = [
        column("Year", "season", IntColumn()),
        column("Event", "event", UrlColumn()),
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

    CONFIG = TableScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_red-flagged_Formula_One_races",
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
        record_factory=record_from_mapping,
    )


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
