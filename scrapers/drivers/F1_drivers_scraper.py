from __future__ import annotations

import re
from typing import Any, Dict, List

from scrapers.F1_table_scraper import F1TableScraper


class F1DriversScraper(F1TableScraper):
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

    column_types = {
        # driver – jako pojedynczy link {text, url}
        "driver": "link",
        # kraj jako zwykły tekst
        "nationality": "text",
        # sezony startów – używamy wbudowanego parsera "seasons"
        "seasons_competed": "seasons",
        # Championships – najpierw "goły" tekst, a potem przerabiamy go w fetch()
        "drivers_championships": "text",
        # punkty jako tekst (bo bywają nawiasy / komentarze)
        "points": "text",
        # reszta = "auto"
    }

    # ------------------------------------------------------------------ #
    #  Pomocniczy parser kolumny "Drivers' Championships"
    # ------------------------------------------------------------------ #
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
                tail = lines[0][m.end():].strip()
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

        # sklejamy resztę w coś w stylu:
        # "2005–2006, 2010, 2012–2013"
        seasons_text = ", ".join(seasons_parts)

        # i używamy dokładnie tej samej logiki, co dla kolumny "seasons"
        # (F1TableScraper._parse_seasons) → lista dictów {year, url}
        seasons = self._parse_seasons(seasons_text)

        return {"count": count, "seasons": seasons}

    # ------------------------------------------------------------------ #
    #  Główne fetch z postprocessingiem
    # ------------------------------------------------------------------ #
    def fetch(self) -> List[Dict[str, Any]]:
        """
        Nadpisujemy fetch(), żeby po bazowym parsowaniu:
        - usunąć symbole z nazw,
        - dodać is_active / is_world_champion,
        - przemapować drivers_championships → {count, seasons[{year,url}, ...]}.
        """
        rows = super().fetch()

        for row in rows:
            # ------------------------------
            # 1) Symbol przy nazwisku (~, *, ^)
            # ------------------------------
            symbol: str | None = None

            name_val = row.get("driver")
            # driver może być dict {"text", "url"} albo zwykłym stringiem
            if isinstance(name_val, dict):
                text = (name_val.get("text") or "").strip()
            else:
                text = (name_val or "").strip()

            if text and text[-1] in ("~", "*", "^"):
                symbol = text[-1]
                cleaned = text[:-1].rstrip()

                if isinstance(name_val, dict):
                    name_val["text"] = cleaned
                    row["driver"] = name_val
                else:
                    row["driver"] = cleaned

            # ------------------------------
            # 2) Czy jest aktywny (startował w 2025)?
            #    Zgodnie z key:
            #      ~ / *  -> startował w 2025
            #    + dodatkowo: jeśli w "Seasons competed" jest "2025"
            # ------------------------------
            # UWAGA: po typie "seasons" seasons_competed jest już listą dictów
            seasons_val = row.get("seasons_competed") or []
            has_2025 = any(
                isinstance(item, dict) and item.get("year") == 2025
                for item in seasons_val
            )

            is_active = has_2025 or symbol in ("~", "*")

            # ------------------------------
            # 3) Parsowanie Drivers' Championships -> dict {count, seasons}
            # ------------------------------
            champs_raw = row.get("drivers_championships")
            champs_info = self._parse_drivers_championships(champs_raw)

            # nadpisujemy kolumnę zparsowanym dict'em
            row["drivers_championships"] = champs_info

            # ------------------------------
            # 4) Czy jest mistrzem świata?
            #    - count > 0
            #    - lub symbol w {~, ^} (oznacza mistrza świata)
            # ------------------------------
            count = champs_info.get("count", 0) or 0
            is_world_champion = (count > 0) or symbol in ("~", "^")

            row["is_active"] = is_active
            row["is_world_champion"] = is_world_champion

        return rows


if __name__ == "__main__":
    scraper = F1DriversScraper(include_urls=True)

    drivers = scraper.fetch()
    print(f"Pobrano rekordów: {len(drivers)}")

    scraper.to_json("../../data/wiki/drivers/f1_drivers.json")
    scraper.to_csv("../../data/wiki/drivers/f1_drivers.csv")

