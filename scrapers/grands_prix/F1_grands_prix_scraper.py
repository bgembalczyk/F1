from __future__ import annotations

import re
from typing import Optional, Sequence, Dict, Any

from bs4 import Tag

from scrapers.F1_table_scraper import F1TableScraper


class F1GrandsPrixScraper(F1TableScraper):
    """
    Scraper dla tabeli 'By race title'
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
    }

    url_columns = ("Race title",)

    # usuwa gwiazdki oznaczające aktywne GP
    _STAR_RE = re.compile(r"[*]")

    # usuwa wszystkie przypisy wikipediowe: [1], [b], [A], [citation needed], etc.
    _REF_RE = re.compile(r"\[\s*[^\]]+\s*\]")

    def _clean_text(self, text: str) -> str:
        """Usuwa *, przypisy [x], oraz trimuje."""
        if not text:
            return text
        t = self._STAR_RE.sub("", text)
        t = self._REF_RE.sub("", t)
        return t.strip()

    def parse_row(
        self,
        row: Tag,
        cells: Sequence[Tag],
        headers: Sequence[str],
    ) -> Optional[Dict[str, Any]]:
        record: Dict[str, Any] = {}
        raw_title: Optional[str] = None  # do statusu active/past

        for header, cell in zip(headers, cells):
            key = self.column_map.get(header, self._normalize_header(header))

            raw_text = cell.get_text(" ", strip=True)

            # zapamiętujemy oryginalne pole z gwiazdką
            if header == "Race title":
                raw_title = raw_text

            clean_text = self._clean_text(raw_text)

            # obsługa URL
            if self.include_urls and header in self.url_columns:
                a = cell.find("a", href=True)
                href = a["href"] if a else None
                url = self._full_url(href)
                if url:
                    record[f"{key}_url"] = url

            record[key] = clean_text

        # race_status: active/past
        if raw_title:
            record["race_status"] = "active" if "*" in raw_title else "past"

        return record


if __name__ == "__main__":
    scraper = F1GrandsPrixScraper(include_urls=True)

    races = scraper.fetch()
    print(f"Pobrano rekordów: {len(races)}")

    scraper.to_json("../../data/wiki/grands_prix/f1_grands_prix_by_title.json")
    scraper.to_csv("../../data/wiki/grands_prix/f1_grands_prix_by_title.csv")
