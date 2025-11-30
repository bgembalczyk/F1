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

    url_columns = ("Circuit",)

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
        # Najpierw używamy bazowej logiki (dict / list[dict] dla linków)
        record = super().parse_row(row, cells, headers)
        if record is None:
            return None

        # --- 1) Ignorujemy kolumnę Map ---
        record.pop("map", None)

        # --- 2) Status toru na podstawie oryginalnej nazwy z tabeli ---
        raw_circuit_name: Optional[str] = None
        for header, cell in zip(headers, cells):
            if header == "Circuit":
                raw_circuit_name = cell.get_text(" ", strip=True)
                break

        if raw_circuit_name:
            if "†" in raw_circuit_name:
                status = "future"
            elif "*" in raw_circuit_name:
                status = "current"
            else:
                status = "former"
            record["circuit_status"] = status
        else:
            record["circuit_status"] = "former"

        # --- 3) Czyścimy nazwę toru z * i † ---
        circuit_val = record.get("circuit")

        if isinstance(circuit_val, dict):
            circuit_val = dict(circuit_val)
            circuit_val["text"] = self._clean_marks(circuit_val.get("text"))
            record["circuit"] = circuit_val
        elif isinstance(circuit_val, str):
            record["circuit"] = self._clean_marks(circuit_val)

        # --- 4) Last length used -> km / mi ---
        raw_length = record.get("last_length_used")
        km = mi = None

        if isinstance(raw_length, str):
            m = self._LENGTH_RE.search(raw_length)
            if m:
                km = m.group("km").strip()
                mi = m.group("mi").strip()

        record["last_length_used_km"] = km
        record["last_length_used_mi"] = mi
        record.pop("last_length_used", None)

        # --- 5) Grands Prix -> ZAWSZE lista dictów ---
        def _normalize_gp_item(item: Any) -> Dict[str, Any]:
            if isinstance(item, dict):
                d = dict(item)
                if isinstance(d.get("text"), str):
                    d["text"] = self._clean_marks(d["text"])
                # jeśli url brak, zostawiamy None / brak klucza
                d.setdefault("url", None)
                return d
            # cokolwiek innego traktujemy jako czysty tekst
            text = self._clean_marks(str(item)) if item is not None else None
            return {"text": text, "url": None}

        gp = record.get("grands_prix")

        if gp is None:
            record["grands_prix"] = []
        elif isinstance(gp, list):
            record["grands_prix"] = [_normalize_gp_item(x) for x in gp]
        else:
            # pojedynczy element (string albo dict) -> lista jednoelementowa
            record["grands_prix"] = [_normalize_gp_item(gp)]

        # --- Season(s) ZAWSZE jako tekst ---
        seasons_val = record.get("seasons")
        if isinstance(seasons_val, dict):
            # wartość była {"text": "...", "url": "..."}
            record["seasons"] = seasons_val.get("text")
        elif isinstance(seasons_val, list):
            # w razie gdyby parser zrobił listę (np. kilka linków)
            # łączymy teksty przecinkami
            record["seasons"] = ", ".join(
                x.get("text") if isinstance(x, dict) else str(x)
                for x in seasons_val
            )
        else:
            # już jest zwykłym stringiem
            record["seasons"] = seasons_val

        return record


if __name__ == "__main__":
    scraper = F1CircuitsScraper(include_urls=True)

    circuits = scraper.fetch()
    print(f"Pobrano rekordów: {len(circuits)}")

    scraper.to_json("../../data/wiki/circuits/f1_circuits.json")
    scraper.to_csv("../../data/wiki/circuits/f1_circuits.csv")
