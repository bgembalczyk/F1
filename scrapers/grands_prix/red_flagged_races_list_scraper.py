from pathlib import Path
from typing import Any, Dict, List

from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.func import FuncColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper


def _restart_status(ctx: ColumnContext) -> Dict[str, Any] | None:
    text = (ctx.clean_text or "").strip()
    if not text:
        return None
    code = text[0].upper()
    mapping = {
        "N": "race_was_not_restarted",
        "Y": "race_was_restarted_over_original_distance",
        "R": "race_was_resumed_to_complete_original_distance",
        "S": "race_was_restarted_or_resumed_without_completing_original_distance",
    }
    return {"code": code, "description": mapping.get(code)}


class _RedFlaggedRacesBaseScraper(F1TableScraper):
    def fetch(self) -> List[Dict[str, Any]]:
        rows = super().fetch()
        for row in rows:
            drivers = row.pop("failed_to_make_restart_drivers", None)
            reason = row.pop("failed_to_make_restart_reason", None)
            if drivers is None and reason is None:
                continue
            row["failed_to_make_restart"] = {
                "drivers": drivers or [],
                "reason": reason,
            }
        return rows


class RedFlaggedWorldChampionshipRacesScraper(_RedFlaggedRacesBaseScraper):
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
            "Drivers",
            "Reason",
        ],
        column_map={
            "Year": "season",
            "Grand Prix": "grand_prix",
            "Lap": "lap",
            "R": "restart_status",
            "Winner": "winner",
            "Incident that prompted red flag": "incident",
            "Drivers": "failed_to_make_restart_drivers",
            "Reason": "failed_to_make_restart_reason",
            "Ref.": "ref",
        },
        columns={
            "season": IntColumn(),
            "grand_prix": UrlColumn(),
            "lap": IntColumn(),
            "restart_status": FuncColumn(_restart_status),
            "winner": DriverColumn(),
            "incident": TextColumn(),
            "failed_to_make_restart_drivers": DriverListColumn(),
            "failed_to_make_restart_reason": TextColumn(),
            "ref": SkipColumn(),
        },
    )


class RedFlaggedNonChampionshipRacesScraper(_RedFlaggedRacesBaseScraper):
    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_red-flagged_Formula_One_races",
        section_id="Non-championship_races",
        expected_headers=[
            "Year",
            "Grand Prix",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
            "Drivers",
            "Reason",
        ],
        column_map={
            "Year": "season",
            "Grand Prix": "grand_prix",
            "Lap": "lap",
            "R": "restart_status",
            "Winner": "winner",
            "Incident that prompted red flag": "incident",
            "Drivers": "failed_to_make_restart_drivers",
            "Reason": "failed_to_make_restart_reason",
            "Ref.": "ref",
        },
        columns={
            "season": IntColumn(),
            "grand_prix": UrlColumn(),
            "lap": IntColumn(),
            "restart_status": FuncColumn(_restart_status),
            "winner": DriverColumn(),
            "incident": TextColumn(),
            "failed_to_make_restart_drivers": DriverListColumn(),
            "failed_to_make_restart_reason": TextColumn(),
            "ref": SkipColumn(),
        },
    )


if __name__ == "__main__":
    run_and_export(
        RedFlaggedWorldChampionshipRacesScraper,
        "grands_prix/f1_red_flagged_world_championship_races.json",
        "grands_prix/f1_red_flagged_world_championship_races.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
    run_and_export(
        RedFlaggedNonChampionshipRacesScraper,
        "grands_prix/f1_red_flagged_non_championship_races.json",
        "grands_prix/f1_red_flagged_non_championship_races.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
