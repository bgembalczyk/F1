from __future__ import annotations

import re
from typing import Dict

from scrapers.F1_table_scraper import F1TableScraper
from scrapers.helpers.columns.column_context import ColumnContext
from scrapers.helpers.columns.columns import SkipColumn, SeasonsColumn, IntColumn, MultiColumn, FuncColumn


def _strip_marks(text: str | None) -> str | None:
    if text is None:
        return None
    return text.replace("*", "").replace("†", "").strip()


# --- małe helpery do FuncColumn ---

def circuit_url_func(ctx: ColumnContext) -> Dict[str, object] | None:
    """
    Wyciąga pierwszy link z nazwy toru i czyści * / † z tekstu.
    """
    if not ctx.links:
        if not ctx.clean_text:
            return None
        return {"text": _strip_marks(ctx.clean_text), "url": None}

    first = dict(ctx.links[0])
    if isinstance(first.get("text"), str):
        first["text"] = _strip_marks(first["text"])
    return first


def circuit_status_func(ctx: ColumnContext) -> str:
    """
    Enum na podstawie znaków w raw_text:
    * -> current, † -> future, brak -> former.
    """
    text = ctx.raw_text or ""
    if "†" in text:
        return "future"
    if "*" in text:
        return "current"
    return "former"


_KM_RE = re.compile(r"(?P<km>[\d\.,]+)\s*km", flags=re.IGNORECASE)
_MI_RE = re.compile(r"(?P<mi>[\d\.,]+)\s*mi", flags=re.IGNORECASE)


def _parse_float_part(text: str, pattern: re.Pattern) -> float | None:
    text = text.replace("\xa0", " ")
    m = pattern.search(text)
    if not m:
        return None
    num = m.group(1).strip().replace(",", "")
    try:
        return float(num)
    except ValueError:
        return None


def length_km_func(ctx: ColumnContext) -> float | None:
    return _parse_float_part(ctx.clean_text or "", _KM_RE)


def length_mi_func(ctx: ColumnContext) -> float | None:
    return _parse_float_part(ctx.clean_text or "", _MI_RE)


def grands_prix_func(ctx: ColumnContext) -> list[Dict[str, object]]:
    """
    Lista GP jako list_of_links, z wyczyszczonym tekstem (* / †).
    """
    result: list[Dict[str, object]] = []
    for link in ctx.links:
        d = dict(link)
        if isinstance(d.get("text"), str):
            d["text"] = _strip_marks(d["text"])
        d.setdefault("url", None)
        result.append(d)
    return result


# ============================================================
#  GŁÓWNY SCRAPER
# ============================================================

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

    # klucz/nagłówek -> kolumna
    columns = {
        # prosto:
        "map": SkipColumn(),
        "seasons": SeasonsColumn(),
        "turns": IntColumn(),
        "grands_prix_held": IntColumn(),

        # Circuit → MultiColumn: (url, status)
        "circuit": MultiColumn(
            {
                "circuit": FuncColumn(circuit_url_func),
                "circuit_status": FuncColumn(circuit_status_func),
            }
        ),

        # Last length used → MultiColumn: (km, mi)
        "last_length_used": MultiColumn(
            {
                "last_length_used_km": FuncColumn(length_km_func),
                "last_length_used_mi": FuncColumn(length_mi_func),
            }
        ),

        # Grands Prix → lista linków
        "grands_prix": FuncColumn(grands_prix_func),
    }


if __name__ == "__main__":
    scraper = F1CircuitsScraper(include_urls=True)

    circuits = scraper.fetch()
    print(f"Pobrano rekordów: {len(circuits)}")

    scraper.to_json("../../data/wiki/circuits/f1_circuits.json")
    scraper.to_csv("../../data/wiki/circuits/f1_circuits.csv")
