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
              "seasons": [<int>, ...]  # lata zdobycia tytułu
          }
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
        # kraj jako zwykły tekst (bez kombinowania z flagami/linkami)
        "nationality": "text",
        # sezony jako tekst (np. "1968–1973, 1975")
        "seasons_competed": "seasons",
        # specjalne traktowanie Championships – najpierw bierzemy czysty tekst,
        # a potem w fetch() robimy z tego dicta {count, seasons}
        "drivers_championships": "text",
        # punkty często mają nawiasy / komentarze, zostawiamy jako tekst
        "points": "text",
        # reszta zostaje na "auto"
    }

    # ------------------------------------------------------------------ #
    #  Pomocniczy parser kolumny "Drivers' Championships"
    # ------------------------------------------------------------------ #
    @staticmethod
    def _parse_drivers_championships(text: str) -> Dict[str, Any]:
        """
        Parsuje tekst z komórki "Drivers' Championships" do postaći:

            {
                "count": <int>,        # liczba tytułów
                "seasons": [<int>, ...]  # lata zdobycia tytułu (np. [2005, 2006])
            }

        Przykładowe wejście:
        - "0"
        - "2\n2005–2006"
        - "7\n1994–1995, 2000–2004"
        """
        text = (text or "").strip()
        if not text:
            return {"count": 0, "seasons": []}

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        count = 0
        rest_parts: List[str] = []

        if lines:
            # pierwsza linia zwykle zawiera samą liczbę tytułów
            m = re.match(r"(\d+)", lines[0])
            if m:
                count = int(m.group(1))
                tail = lines[0][m.end():].strip()
                if tail:
                    rest_parts.append(tail)
                # pozostałe linie traktujemy jako części z latami
                rest_parts.extend(lines[1:])
            else:
                # fallback – spróbuj wyciągnąć jakąś liczbę z całego tekstu
                m2 = re.search(r"\d+", text)
                if m2:
                    count = int(m2.group(1))
                # lata z pozostałych linii (jeśli są)
                rest_parts = lines[1:] if len(lines) > 1 else []
        else:
            # gdyby coś poszło nie tak z lines
            m2 = re.search(r"\d+", text)
            if m2:
                count = int(m2.group(1))

        # jeśli count == 0, to lista sezonów może nas nie interesować
        if count == 0 or not rest_parts:
            return {"count": count, "seasons": []}

        years: List[int] = []

        for part in rest_parts:
            # normalizujemy różne "–" na zwykły "-"
            part = part.replace("–", "-").replace("—", "-")
            # dzielimy po przecinkach / średnikach
            for chunk in re.split(r"[,\;]", part):
                chunk = chunk.strip()
                if not chunk:
                    continue

                # zakresy typu "2005-2006"
                if "-" in chunk:
                    rng = re.match(r"(\d{4})\s*-\s*(\d{4})", chunk)
                    if rng:
                        start = int(rng.group(1))
                        end = int(rng.group(2))
                        if start <= end:
                            years.extend(range(start, end + 1))
                        else:
                            # na wszelki wypadek, gdyby kolejność była odwrócona
                            years.extend([start, end])
                    else:
                        # fallback: wyciągnij pojedyncze lata z kawałka
                        years.extend(int(y) for y in re.findall(r"\d{4}", chunk))
                else:
                    # pojedynczy rok
                    y = re.search(r"\d{4}", chunk)
                    if y:
                        years.append(int(y.group(0)))

        # usuwamy duplikaty z zachowaniem kolejności
        seen = set()
        seasons: List[int] = []
        for y in years:
            if y not in seen:
                seen.add(y)
                seasons.append(y)

        return {"count": count, "seasons": seasons}

    # ------------------------------------------------------------------ #
    #  Główne fetch z postprocessingiem
    # ------------------------------------------------------------------ #
    def fetch(self) -> List[Dict[str, Any]]:
        """
        Nadpisujemy fetch(), żeby po bazowym parsowaniu:
        - usunąć symbole z nazw,
        - dodać is_active / is_world_champion,
        - przemapować drivers_championships → {count, seasons}.
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
            seasons_text = str(row.get("seasons_competed") or "")
            has_2025 = "2025" in seasons_text

            is_active = has_2025 or symbol in ("~", "*")

            # ------------------------------
            # 3) Parsowanie Drivers' Championships -> dict
            # ------------------------------
            champs_raw = row.get("drivers_championships")
            champs_info = self._parse_drivers_championships(str(champs_raw or ""))

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

