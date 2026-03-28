from scrapers.base.records import record_from_mapping
from scrapers.drivers.columns.driver import DriverColumn
from scrapers.drivers.columns.driver_list import DriverListColumn
from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.table.columns.types import DriverColumn
from scrapers.base.table.columns.types import DriverListColumn
from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import SkipColumn
from scrapers.base.table.columns.types import TextColumn
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.grands_prix.columns.restart_status import RestartStatusColumn
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

    CONFIG = build_scraper_config(
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
        record_factory=RECORD_FACTORIES.mapping(),
    )


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
