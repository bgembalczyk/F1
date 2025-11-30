from __future__ import annotations

import re
from typing import Any, Dict, Optional, Sequence

from bs4 import Tag

from scrapers.F1_table_scraper import F1TableScraper


class F1CircuitsScraper(F1TableScraper):
    """
    Lista torów F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_circuits
    (duża tabela 'Circuits')
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

    # typy kolumn (klucze mogą być nagłówkami)
    column_types = {
        "Map": "skip",          # w ogóle pomijamy
        "Season(s)": "seasons", # specjalny parser sezonów -> lista dict{year,url}
        "Grands Prix": "list_of_links",  # upewnia się, że zawsze jest lista
    }

    _LENGTH_RE = re.compile(
        r"(?P<km>[\d\.,]+)\s*km.*?(?P<mi>[\d\.,]+)\s*mi",
        flags=re.IGNORECASE,
    )

    @staticmethod
    def _clean_marks(text: str | None) -> str | None:
        if text is None:
            return None
        return text.replace("*", "").replace("†", "").strip()

    def parse_row(
        self,
        row: Tag,
        cells: Sequence[Tag],
        headers: Sequence[str],
    ) -> Optional[Dict[str, Any]]:
        # bazowa logika: kolumny, typy (w tym skip + seasons),
        # auto linki, czysty tekst bez [przypisów]
        record = super().parse_row(row, cells, headers)
        if record is None:
            return None

        # --- 1) Status toru na podstawie ORYGINALNEJ nazwy z tabeli ---
        raw_circuit_name: Optional[str] = None
        for header, cell in zip(headers, cells):
            if header == "Circuit":
                raw_circuit_name = cell.get_text(" ", strip=True).replace("\xa0", " ")
                break

        if raw_circuit_name:
            if "†" in raw_circuit_name:
                status = "future"
            elif "*" in raw_circuit_name:
                status = "current"
            else:
                status = "former"
        else:
            status = "former"

        record["circuit_status"] = status

        # --- 2) Czyścimy nazwę toru z * i † ---
        circuit_val = record.get("circuit")
        if isinstance(circuit_val, dict):
            cleaned = dict(circuit_val)
            cleaned["text"] = self._clean_marks(cleaned.get("text"))
            record["circuit"] = cleaned
        elif isinstance(circuit_val, str):
            record["circuit"] = self._clean_marks(circuit_val)

        # --- 3) Last length used -> km / mi ---
        raw_length = record.get("last_length_used")
        km = mi = None

        if isinstance(raw_length, str):
            raw_norm = raw_length.replace("\xa0", " ")
            m = self._LENGTH_RE.search(raw_norm)
            if m:
                km = m.group("km").strip()
                mi = m.group("mi").strip()

        record["last_length_used_km"] = km
        record["last_length_used_mi"] = mi
        record.pop("last_length_used", None)

        # --- 4) Grands Prix -> upewniamy się, że lista dictów {text, url} bez * / † ---
        def _normalize_gp_item(item: Any) -> Dict[str, Any]:
            if isinstance(item, dict):
                d = dict(item)
                if isinstance(d.get("text"), str):
                    d["text"] = self._clean_marks(d["text"])
                d.setdefault("url", None)
                return d
            text = self._clean_marks(str(item)) if item is not None else None
            return {"text": text, "url": None}

        gp = record.get("grands_prix")
        if gp is None:
            record["grands_prix"] = []
        elif isinstance(gp, list):
            record["grands_prix"] = [_normalize_gp_item(x) for x in gp]
        else:
            record["grands_prix"] = [_normalize_gp_item(gp)]

        # --- 5) seasons jest już listą dictów {year, url} z F1TableScraper (typ 'seasons') ---
        # nic więcej nie trzeba robić

        return record


if __name__ == "__main__":
    scraper = F1CircuitsScraper(include_urls=True)

    circuits = scraper.fetch()
    print(f"Pobrano rekordów: {len(circuits)}")

    scraper.to_json("../../data/wiki/circuits/f1_circuits.json")
    scraper.to_csv("../../data/wiki/circuits/f1_circuits.csv")
