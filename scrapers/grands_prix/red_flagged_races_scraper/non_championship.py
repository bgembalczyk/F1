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
from scrapers.grands_prix.columns.restart_status import RestartStatusColumn
from scrapers.grands_prix.red_flagged_races_scraper.base import (
    RedFlaggedRacesBaseScraper,
)


class RedFlaggedNonChampionshipRacesScraper(RedFlaggedRacesBaseScraper):
    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_red-flagged_Formula_One_races",
        section_id="Non-championship_races",
        expected_headers=[
            "Year",
            "Event",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
            "Failed to make the restart",
        ],
        column_map={
            "Year": "season",
            "Event": "event",
            "Lap": "lap",
            "R": "restart_status",
            "Winner": "winner",
            "Incident that prompted red flag": "incident",
            "Failed to make the restart - Drivers": "failed_to_make_restart_drivers",
            "Failed to make the restart - Reason": "failed_to_make_restart_reason",
            "Ref.": "ref",
        },
        columns={
            "season": IntColumn(),
            "event": UrlColumn(),
            "lap": IntColumn(),
            "restart_status": RestartStatusColumn(),
            "winner": DriverColumn(),
            "incident": TextColumn(),
            "failed_to_make_restart_drivers": DriverListColumn(),
            "failed_to_make_restart_reason": TextColumn(),
            "ref": SkipColumn(),
        },
        record_factory=record_from_mapping,
    )


if __name__ == "__main__":
    run_and_export(
        RedFlaggedNonChampionshipRacesScraper,
        "grands_prix/f1_red_flagged_non_championship_races.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
