from __future__ import annotations

from pathlib import Path
from typing import Any, List

from models.scrape_types import (
    DriverChampionshipsPayload,
    DriverRow,
)  # typing-only, ale OK
from models.services.driver_service import DriverService
from scrapers.base.registry import register_scraper
from scrapers.base.run import run_scraper_by_name
from scrapers.base.table.columns.types.bool import BoolColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper


@register_scraper(
    "drivers",
    "drivers/f1_drivers.json",
    "drivers/f1_drivers.csv",
)
class F1DriversListScraper(F1TableScraper):
    """
    Scraper listy kierowców F1 z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_drivers

    Dodatkowo:
    - is_active: (~ lub * na końcu raw_text w kolumnie "Driver name")
    - is_world_champion: (~ lub ^ na końcu raw_text w kolumnie "Driver name")
    - drivers_championships: parsowane do dict {count, seasons}
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_drivers",
        section_id="Drivers",
        expected_headers=[
            "Driver name",
            "Nationality",
            "Seasons competed",
            "Drivers' Championships",
        ],
        column_map={
            "Driver name": "driver",
            "Nationality": "nationality",
            "Seasons competed": "seasons_competed",
            "Drivers' Championships": "drivers_championships",
            "Race entries": "race_entries",
            "Race starts": "race_starts",
            "Pole positions": "pole_positions",
            "Race wins": "race_wins",
            "Podiums": "podiums",
            "Fastest laps": "fastest_laps",
            "Points": "points",
        },
        columns={
            "driver": MultiColumn(
                {
                    "driver": UrlColumn(),
                    "is_active": BoolColumn(
                        lambda ctx: (ctx.raw_text or "").strip().endswith(("~", "*"))
                    ),
                    "is_world_champion": BoolColumn(
                        lambda ctx: (ctx.raw_text or "").strip().endswith(("~", "^"))
                    ),
                }
            ),
            "nationality": TextColumn(),
            "seasons_competed": SeasonsColumn(),
            "drivers_championships": TextColumn(),  # zparsujemy ręcznie w fetch()
            "race_entries": IntColumn(),
            "race_starts": IntColumn(),
            "pole_positions": IntColumn(),
            "race_wins": IntColumn(),
            "podiums": IntColumn(),
            "fastest_laps": IntColumn(),
            "points": TextColumn(),
        },
    )

    @staticmethod
    def _parse_drivers_championships(raw: Any) -> DriverChampionshipsPayload:
        """
        Deleguje parsowanie do DriverService.parse_championships.

        Wejście (po TextColumn) bywa np.:
        - "0"
        - "2\\n2005–2006"
        - "7\\n1994–1995, 2000–2004"
        """
        return DriverService.parse_championships(raw)  # type: ignore[return-value]

    def fetch(self) -> List[DriverRow]:
        rows = super().fetch()

        for row in rows:
            champs_raw = row.get("drivers_championships")
            row["drivers_championships"] = self._parse_drivers_championships(champs_raw)

        # runtime: nadal zwracamy list[dict], typy są dla Ciebie
        return rows  # type: ignore[return-value]


if __name__ == "__main__":
    run_scraper_by_name("drivers", Path("../../data/wiki"), include_urls=True)
