from __future__ import annotations

import re
from typing import Any, Dict, List

from scrapers.base.table.columns.types.bool import BoolColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.helpers.utils import parse_seasons
from scrapers.base.table.scraper import F1TableScraper


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

    data_resource = "drivers"
    data_file_stem = "f1_drivers"
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
        """
        Parsuje tekst z komórki "Drivers' Championships" do postaci:

            {
                "count": <int>,              # liczba tytułów
                "seasons": [ {year, url}, ... ]  # sezony zdobycia tytułu
            }

        Przykładowe wejście (raw, po bazowym parsowaniu typu "text"):
        - "0"
        - "2\\n2005–2006"
        - "7\\n1994–1995, 2000–2004"
        """
        text = (str(raw) if raw is not None else "").strip()
        if not text:
            return {"count": 0, "seasons": []}

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        count = 0
        seasons_parts: List[str] = []

        if lines:
            # pierwsza linia zwykle zaczyna się od liczby tytułów
            m = re.match(r"(\d+)", lines[0])
            if m:
                count = int(m.group(1))
                tail = lines[0][m.end() :].strip()
                if tail:
                    seasons_parts.append(tail)
                # reszta linii traktujemy jako kolejne fragmenty z latami
                seasons_parts.extend(lines[1:])
            else:
                # fallback – spróbuj wyciągnąć liczbę z całego tekstu
                m2 = re.search(r"\d+", text)
                if m2:
                    count = int(m2.group(1))
                seasons_parts = lines[1:] if len(lines) > 1 else []
        else:
            # gdyby coś poszło nie tak z lines
            m2 = re.search(r"\d+", text)
            if m2:
                count = int(m2.group(1))

        # jeśli count == 0 albo nie ma fragmentu z latami – nie ma sezonów
        if count == 0 or not seasons_parts:
            return {"count": count, "seasons": []}

        seasons_text = ", ".join(seasons_parts)
        seasons = parse_seasons(seasons_text)

        return {"count": count, "seasons": seasons}

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
