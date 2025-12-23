"""Funkcje pomocnicze do normalizacji danych torów."""

import re
from typing import Any

from scrapers.base.helpers.text_normalization import add_unique_name


def extract_circuit_names(
    raw: dict[str, Any], infobox: dict[str, Any], normalized: dict[str, Any]
) -> dict[str, Any]:
    """Ekstrakcja nazwy i poprzednich nazw toru."""
    circuit = raw.get("circuit") or {}
    name_set: set[str] = set()
    name_list: list[str] = []

    # 1) circuit[text] -> name.list
    add_unique_name(name_set, name_list, circuit.get("text"))

    # 2) infobox.title + infobox.normalized.name
    if infobox:
        add_unique_name(name_set, name_list, infobox.get("title"))
    if normalized:
        add_unique_name(name_set, name_list, normalized.get("name"))

    # 3) former_names -> name.former_names
    former_names: list[dict[str, Any]] = []
    if normalized:
        history_norm = normalized.get("history") or {}
        former_names = history_norm.get("former_names") or []

    return {
        "list": name_list,
        "former_names": former_names,
    }


def extract_circuit_url(
    raw: dict[str, Any], details: dict[str, Any] | None
) -> str | None:
    """Zwraca circuit[url], ale None jeśli details == None."""
    if details is None:
        return None
    circuit = raw.get("circuit") or {}
    return circuit.get("url")


def extract_circuit_location(
    raw: dict[str, Any], normalized: dict[str, Any]
) -> dict[str, Any]:
    """
    Buduje location = { places, coordinates }.
    - places z raw.location.places (lista),
    - coordinates z infobox.normalized.location.coordinates (dict).
    """
    location_raw = raw.get("location") or {}
    places = location_raw.get("places") or []

    coordinates = None
    if normalized:
        loc_norm = normalized.get("location") or {}
        coordinates = loc_norm.get("coordinates")

    return {
        "places": places,
        "coordinates": coordinates,
    }


def extract_circuit_grade_and_history(
    normalized: dict[str, Any],
) -> tuple[Any, Any]:
    """Zwraca (fia_grade, history_events)."""
    fia_grade = None
    history_events = None

    if normalized:
        specs = normalized.get("specs") or {}
        fia_grade = specs.get("fia_grade")

        history_norm = normalized.get("history") or {}
        history_events = history_norm.get("events")

    return fia_grade, history_events


def extract_infobox_layouts(infobox: dict[str, Any]) -> list[dict[str, Any]]:
    """Pobiera layouts z infobox."""
    if not infobox:
        return []

    normalized = infobox.get("normalized") or {}
    layouts = normalized.get("layouts") or []

    result: list[dict[str, Any]] = []
    for lay in layouts:
        lay_copy: dict[str, Any] = dict(lay)

        # race_lap_record -> race_lap_records (lista)
        rlr = lay_copy.pop("race_lap_record", None)
        if rlr is not None:
            if not isinstance(rlr, list):
                rlr = [rlr]
            lay_copy["race_lap_records"] = list(rlr)

        result.append(lay_copy)

    return result


def parse_table_layout_info(table_layout: str) -> tuple[float | None, str | None]:
    """
    Parsuje 'layout' z tabeli lap_records (np. '5.412 km (3.363 mi)').
    Zwraca (length_km, direction).
    """
    length_km = None
    direction = None

    if not table_layout:
        return length_km, direction

    # Wyciągnij float przed 'km'
    m = re.search(r"([\d.]+)\s*km", table_layout, re.IGNORECASE)
    if m:
        try:
            length_km = float(m.group(1))
        except ValueError:
            pass

    # Szukaj direction (clockwise/anticlockwise/anti-clockwise)
    s = table_layout.lower()
    if "clockwise" in s:
        if "anti" in s:
            direction = "anti-clockwise"
        else:
            direction = "clockwise"

    return length_km, direction


def find_layout_for_table(
    table: dict[str, Any],
    layouts: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Próbuje znaleźć layout pasujący do tabeli.

    Zwraca layout, do którego można dodać rekordy z tej tabeli,
    albo None, jeśli nie znaleziono dopasowania.
    """
    table_layout = table.get("layout") or ""
    table_length_km, table_direction = parse_table_layout_info(table_layout)

    if not layouts:
        return None

    best_match = None
    best_score = 0

    for lay in layouts:
        score = 0

        lay_length_km = lay.get("length_km")
        lay_direction = lay.get("direction")

        # dopasowanie długości (dokładne w przedziale ±0.01 km)
        if table_length_km is not None and lay_length_km is not None:
            if abs(table_length_km - lay_length_km) < 0.01:
                score += 10

        # dopasowanie direction
        if table_direction and lay_direction:
            if table_direction.lower() == lay_direction.lower():
                score += 5

        if score > best_score:
            best_score = score
            best_match = lay

    # akceptujemy tylko jeśli score > 0
    return best_match if best_score > 0 else None


def merge_tables_into_layouts(
    tables: list[dict[str, Any]],
    layouts: list[dict[str, Any]],
) -> None:
    """
    Łączy dane z tables (lap_records) do odpowiednich layoutów.

    Modyfikuje layouts in-place.
    """
    for table in tables:
        records = table.get("lap_records") or []
        if not records:
            continue

        target_layout = find_layout_for_table(table, layouts)
        if target_layout is not None:
            existing = target_layout.setdefault("race_lap_records", [])
            existing.extend(records)

