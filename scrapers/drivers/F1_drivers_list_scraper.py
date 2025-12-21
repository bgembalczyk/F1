from __future__ import annotations

from typing import Any, Dict

from models.services.driver_service import DriverService
from scrapers.base.registry import register_scraper
from scrapers.base.table.columns.types.bool import BoolColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.run import run_and_export


@register_scraper(
    "drivers",
    "drivers/f1_drivers.json",
    "drivers/f1_drivers.csv",
)
class F1DriversListScraper(F1TableScraper):
    """
    Scraper listy kierowców F1 z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_drivers

    Parsuje główną tabelę w sekcji "Drivers" i dodatkowo:
    - czyści symbol (~, *, ^) z kolumny 'Driver name',
    - dodaje pola:
        * is_active          – czy kierowca startował w sezonie 2025,
        * is_world_champion  – czy kierowca jest mistrzem świata,
    - przetwarza kolumnę 'Drivers' Championships' do dicta:
        * drivers_championships = {
              "count": <int>,
              "seasons": [
                  {"year": 2005, "url": "..."},
                  {"year": 2006, "url": "..."},
                  ...
              ]
          }
      gdzie "seasons" są parsowane tą samą logiką co kolumna seasons_competed
      (typ kolumny "seasons" w F1TableScraper).
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_drivers"
    section_id = "Drivers"

    expected_headers = [
        "Driver name",
        "Nationality",
        "Seasons competed",
        "Drivers' Championships",
    ]

    column_map = {
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
    }

    columns = {
        "driver": MultiColumn(
            {
                "driver": UrlColumn(),
                # bool na podstawie raw_text – nowa BoolColumn
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
        "drivers_championships": TextColumn(),
        "race_entries": IntColumn(),
        "race_starts": IntColumn(),
        "pole_positions": IntColumn(),
        "race_wins": IntColumn(),
        "podiums": IntColumn(),
        "fastest_laps": IntColumn(),
        "points": TextColumn(),
    }

    # =====================================================================
    #  Parsowanie kolumny Drivers' Championships
    # =====================================================================

    def _parse_drivers_championships(self, raw: Any) -> Dict[str, Any]:
        return DriverService.parse_championships(raw)

    # =====================================================================
    #  Główne fetch
    # =====================================================================

    def fetch(self) -> List[Dict[str, Any]]:
        """
        Minimalne fetch:
        - NIE nadpisujemy is_active / is_world_champion — to robi BoolColumn.
        - Parsujemy tylko kolumnę 'drivers_championships' do dict {count, seasons}.
        """
        rows = super().fetch()

        for row in rows:
            champs_raw = row.get("drivers_championships")
            champs_info = self._parse_drivers_championships(champs_raw)
            row["drivers_championships"] = champs_info

        return rows


if __name__ == "__main__":
    run_and_export(
        F1DriversListScraper,
        "../../data/wiki/drivers/f1_drivers.json",
        "../../data/wiki/drivers/f1_drivers.csv",
        include_urls=True,
    )
