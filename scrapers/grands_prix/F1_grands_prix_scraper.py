from __future__ import annotations

import re
from typing import Optional, Sequence, Dict, Any, List

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

    expected_headers = [
        "Race title",
        "Years held",
    ]

    column_map = {
        "Race title": "race_title",
        "Years held": "years_held",
        "Races held": "races_held",
        "Country": "country",
    }

    url_columns = ("Race title",)

    # usuwamy gwiazdki z wyświetlanej nazwy
    _STAR_RE = re.compile(r"\*")

    # usuwamy przypisy Wikipedii: [1], [b], [note 3], [citation needed], itd.
    _REF_RE = re.compile(r"\[\s*[^]]+\s*]")

    def _clean_title_text(self, text: str | None) -> str | None:
        """Usuń gwiazdki i przypisy w nawiasach kwadratowych z nazwy GP."""
        if text is None:
            return None
        t = self._STAR_RE.sub("", text)
        t = self._REF_RE.sub("", t)
        return t.strip()

    def _normalize_country_to_list(self, value: Any) -> List[Dict[str, Any]]:
        """
        Zwraca zawsze listę słowników {text, url}.
        """
        countries: List[Dict[str, Any]] = []

        if value is None:
            return countries

        if isinstance(value, list):
            items = value
        else:
            items = [value]

        for item in items:
            if isinstance(item, dict):
                text = item.get("text")
                url = item.get("url")
            else:
                text = str(item) if item is not None else None
                url = None

            # pomijamy całkiem puste
            if text is None or str(text).strip() == "":
                continue

            countries.append(
                {
                    "text": str(text),
                    "url": url,
                }
            )

        return countries

    def parse_row(
        self,
        row: Tag,
        cells: Sequence[Tag],
        headers: Sequence[str],
    ) -> Optional[Dict[str, Any]]:
        # najpierw bazowa logika (dict / list[dict] dla linków itp.)
        record = super().parse_row(row, cells, headers)
        if record is None:
            return None

        # --- 1) Race title: status + czyszczenie tekstu ---
        raw_title: Optional[str] = None
        for header, cell in zip(headers, cells):
            if header == "Race title":
                raw_title = cell.get_text(" ", strip=True)
                break

        # status active/past na podstawie gwiazdki w oryginalnym tekście
        if raw_title:
            record["race_status"] = "active" if "*" in raw_title else "past"
        else:
            record["race_status"] = "past"

        # wyczyść race_title z gwiazdek i przypisów
        rt = record.get("race_title")
        if isinstance(rt, dict):
            rt = dict(rt)
            rt["text"] = self._clean_title_text(rt.get("text"))
            record["race_title"] = rt
        elif isinstance(rt, str):
            record["race_title"] = self._clean_title_text(rt)

        # --- 2) Years held: ZAWSZE tekst ---
        years_val = record.get("years_held")
        if isinstance(years_val, dict):
            # {"text": "...", "url": "..."}
            record["years_held"] = years_val.get("text")
        elif isinstance(years_val, list):
            # np. lista dictów; łączymy teksty przecinkami
            parts: list[str] = []
            for item in years_val:
                if isinstance(item, dict):
                    parts.append(str(item.get("text", "")))
                else:
                    parts.append(str(item))
            record["years_held"] = ", ".join(p for p in parts if p)
        else:
            # już jest stringiem albo None
            record["years_held"] = years_val

        # --- 3) Country: ZAWSZE lista ---
        record["country"] = self._normalize_country_to_list(record.get("country"))

        return record


if __name__ == "__main__":
    scraper = F1GrandsPrixScraper(include_urls=True)

    races = scraper.fetch()
    print(f"Pobrano rekordów: {len(races)}")

    scraper.to_json("../../data/wiki/grands_prix/f1_grands_prix_by_title.json")
    scraper.to_csv("../../data/wiki/grands_prix/f1_grands_prix_by_title.csv")
