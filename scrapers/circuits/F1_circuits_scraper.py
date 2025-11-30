from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence

from bs4 import Tag

from scrapers.F1_table_scraper import F1TableScraper


class F1CircuitsScraper(F1TableScraper):
    """
    Lista torów F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_circuits
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_circuits"
    section_id = "Circuits"

    expected_headers = [
        "Circuit",
        "Type",
        "Location",
        "Country",
    ]

    column_map = {
        "Circuit": "circuit",
        "Map": "map",
        "Type": "type",
        "Direction": "direction",
        "Location": "location",
        "Country": "country",
        "Last length used": "last_length_used",
        "Turns": "turns",
        "Grands Prix": "grands_prix",
        "Season(s)": "seasons",
        "Grands Prix held": "grands_prix_held",
    }

    url_columns = ("Circuit",)

    _LENGTH_RE = re.compile(
        r"(?P<km>[\d\.,]+)\s*km.*?(?P<mi>[\d\.,]+)\s*mi",
        flags=re.IGNORECASE,
    )

    # usuwamy oznaczenia typu "*", "†"
    _MARK_RE = re.compile(r"[*\u2020]")  # \u2020 = †

    # ------------------------------
    # nowa metoda -> określa status
    # ------------------------------
    def _detect_circuit_status(self, raw_name: str) -> str:
        """
        Zgodnie z legendą Wikipedii:
        *  -> current
        †  -> future
        brak -> former
        """
        if "*" in raw_name:
            return "current"
        if "†" in raw_name:
            return "future"
        return "former"

    # ------------------------------
    # nadpisany parse_row
    # ------------------------------
    def parse_row(
        self,
        row: Tag,
        cells: Sequence[Tag],
        headers: Sequence[str],
    ) -> Optional[Dict[str, Any]]:
        record: Dict[str, Any] = {}
        raw_circuit_name: str | None = None  # do statusu

        for header, cell in zip(headers, cells):
            if header == "Map":
                continue  # ignorujemy

            key = self.column_map.get(header, self._normalize_header(header))
            text = cell.get_text(" ", strip=True)

            # zapamiętujemy oryginalną nazwę toru
            if header == "Circuit":
                raw_circuit_name = text

            # usuwamy oznaczenia (*, †)
            clean_text = self._MARK_RE.sub("", text).strip()

            # --- location / country ---
            if header in ("Location", "Country"):
                url = None
                if self.include_urls:
                    a = cell.find("a", href=True)
                    if a:
                        url = self._full_url(a["href"])

                record[key] = {
                    "text": clean_text or None,
                    "url": url,
                }
                continue

            # --- last length used ---
            if header == "Last length used":
                raw = (clean_text or "").replace("\xa0", " ")
                m = self._LENGTH_RE.search(raw)
                km = m.group("km").strip() if m else None
                mi = m.group("mi").strip() if m else None

                record["last_length_used_km"] = km
                record["last_length_used_mi"] = mi
                continue

            # --- grands prix ---
            if header == "Grands Prix":
                gps: List[Dict[str, Any]] = []

                for a in cell.find_all("a"):
                    gp_text = a.get_text(" ", strip=True)
                    gp_text = self._MARK_RE.sub("", gp_text).strip()
                    if not gp_text:
                        continue

                    url = self._full_url(a["href"]) if self.include_urls else None
                    gps.append(
                        {
                            "text": gp_text,
                            "url": url,
                        }
                    )

                record[key] = gps
                continue

            # --- pozostałe kolumny ---
            if self.include_urls and header in self.url_columns:
                a = cell.find("a", href=True)
                href = a["href"] if a else None
                full = self._full_url(href)
                if full:
                    record[f"{key}_url"] = full

            record[key] = clean_text

        # --- dodajemy circuit_status ---
        if raw_circuit_name:
            record["circuit_status"] = self._detect_circuit_status(raw_circuit_name)

        return record


if __name__ == "__main__":
    scraper = F1CircuitsScraper(include_urls=True)

    circuits = scraper.fetch()
    print(f"Pobrano rekordów: {len(circuits)}")

    scraper.to_json("../../data/wiki/circuits/f1_circuits.json")
    scraper.to_csv("../../data/wiki/circuits/f1_circuits.csv")
