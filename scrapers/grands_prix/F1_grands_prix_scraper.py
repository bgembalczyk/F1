from __future__ import annotations

import re
from typing import Optional, Sequence, Dict, Any

from bs4 import Tag

from scrapers.F1_table_scraper import F1TableScraper


class F1GrandsPrixScraper(F1TableScraper):
    """
    Uproszczony scraper np. dla tabeli 'By race title'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix"
    section_id = "By_race_title"

    # podzbiór nagłówków – do znalezienia właściwej tabeli
    expected_headers: Sequence[str] = [
        "Race title",
        "Years held",
    ]

    # mapowanie nagłówek -> klucz w dict
    column_map: Dict[str, str] = {
        "Race title": "race_title",
        "Years held": "years_held",
        "Races held": "races_held",
        "Country": "country",
    }

    # typy kolumn już po mapowaniu (po stronie dict-a)
    # - years_held: zawsze tekst (bez kombinacji z listami / dictami)
    # - country: zawsze lista linków {text, url}
    column_types: Dict[str, str] = {
        "race_title": "link",
        "years_held": "seasons",
        "country": "list_of_links",
    }

    # usuwamy gwiazdki z wyświetlanej nazwy (status aktywne/past zostaje w osobnym polu)
    _STAR_RE = re.compile(r"\*")

    def _clean_title_text(self, text: str | None) -> str | None:
        """Usuń gwiazdki z nazwy GP + standardowe czyszczenie tekstu."""
        if text is None:
            return None
        t = self._STAR_RE.sub("", text)
        # dodatkowe sprzątanie (whitespace, przypisy) robi helper z klasy bazowej
        return self._clean_text(t)

    def parse_row(
        self,
        row: Tag,
        cells: Sequence[Tag],
        headers: Sequence[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Korzystamy z bazowego parse_row (linki, list_of_links, seasons, itp.),
        a potem tylko:
        - ustawiamy race_status na podstawie oryginalnego tytułu (z gwiazdką),
        - czyścimy race_title z gwiazdek.
        """
        # najpierw standardowe parsowanie tabeli
        record = super().parse_row(row, cells, headers)
        if record is None:
            return None

        # --- Race title: znajdź oryginalny tekst z komórki (z gwiazdką) ---
        raw_title: Optional[str] = None
        for header, cell in zip(headers, cells):
            if header == "Race title":
                raw_title = cell.get_text(" ", strip=True)
                break

        # status: aktywne GP ma gwiazdkę przy nazwie
        if raw_title:
            record["race_status"] = "active" if "*" in raw_title else "past"
        else:
            record["race_status"] = "past"

        # --- wyczyść race_title z gwiazdek (i ewentualnych przypisów) ---
        rt = record.get("race_title")

        if isinstance(rt, dict):
            # zachowaj URL, popraw tylko tekst
            new_rt = dict(rt)
            new_rt["text"] = self._clean_title_text(new_rt.get("text"))
            record["race_title"] = new_rt
        elif isinstance(rt, str):
            record["race_title"] = self._clean_title_text(rt)

        return record


if __name__ == "__main__":
    scraper = F1GrandsPrixScraper(include_urls=True)

    races = scraper.fetch()
    print(f"Pobrano rekordów: {len(races)}")

    scraper.to_json("../../data/wiki/grands_prix/f1_grands_prix_by_title.json")
    scraper.to_csv("../../data/wiki/grands_prix/f1_grands_prix_by_title.csv")
