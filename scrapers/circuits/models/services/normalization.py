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


def add_place(
    text: str | None,
    url: str | None,
    places: list[dict[str, Any]],
    seen_places: set[str],
) -> None:
    """
    Dodaje miejsce do listy, jeśli nie jest duplikatem.

    Args:
        text: Tekst nazwy miejsca
        url: Opcjonalny URL
        places: Lista miejsc do modyfikacji in-place
        seen_places: Zbiór już widzianych miejsc (case-insensitive) do modyfikacji in-place
    """
    if not text:
        return
    key = text.strip().lower()
    if not key or key in seen_places:
        return
    seen_places.add(key)
    entry: dict[str, Any] = {"text": text.strip()}
    if url:
        entry["url"] = url
    places.append(entry)


def loc_sort_key(item: tuple[str, Any]) -> int:
    """
    Funkcja sortowania dla elementów lokalizacji (używana do sortowania po liczbach w kluczach).

    Args:
        item: Krotka (klucz, wartość) ze słownika

    Returns:
        Liczba z końca klucza lub 0 jeśli brak
    """
    match = re.search(r"(\d+)$", item[0])
    return int(match.group(1)) if match else 0


def extract_circuit_location(
    raw: dict[str, Any], normalized: dict[str, Any]
) -> dict[str, Any]:
    """
    Buduje location = { places, coordinates }.
    - places z raw.location (lista/dict/string) oraz z infobox.normalized.location,
    - coordinates z infobox.normalized.coordinates (dict).
    - dodaje również raw.country do places (jeśli jeszcze go tam nie ma).
    """
    location_raw = raw.get("location")
    places: list[dict[str, Any]] = []
    seen_places: set[str] = set()

    if isinstance(location_raw, dict):
        raw_places = location_raw.get("places")
        if isinstance(raw_places, list):
            for place in raw_places:
                if isinstance(place, dict):
                    add_place(place.get("text"), place.get("url"), places, seen_places)
                elif isinstance(place, str):
                    add_place(place, None, places, seen_places)
        elif "text" in location_raw:
            add_place(
                location_raw.get("text"), location_raw.get("url"), places, seen_places
            )
        elif "name" in location_raw:
            add_place(location_raw.get("name"), None, places, seen_places)
    elif isinstance(location_raw, list):
        for place in location_raw:
            if isinstance(place, dict):
                add_place(place.get("text"), place.get("url"), places, seen_places)
            elif isinstance(place, str):
                add_place(place, None, places, seen_places)
    elif isinstance(location_raw, str):
        add_place(location_raw, None, places, seen_places)

    coordinates = None
    loc_norm = None
    if normalized:
        coordinates = normalized.get("coordinates")
        loc_norm = normalized.get("location") or {}
        if coordinates is None and isinstance(loc_norm, dict):
            coordinates = loc_norm.get("coordinates")

    if isinstance(loc_norm, dict):
        for _, comp in sorted(loc_norm.items(), key=loc_sort_key):
            if isinstance(comp, dict):
                link = comp.get("link") or {}
                add_place(
                    comp.get("text") or link.get("text"),
                    link.get("url"),
                    places,
                    seen_places,
                )
            else:
                add_place(str(comp), None, places, seen_places)

    # Dodaj country z raw, jeśli jeszcze go tam nie ma
    country = raw.get("country")
    if country:
        if isinstance(country, dict):
            add_place(country.get("text"), country.get("url"), places, seen_places)
        elif isinstance(country, str):
            add_place(country, None, places, seen_places)

    return {
        "places": places,
        "coordinates": coordinates,
    }


def extract_fia_grade(normalized: dict[str, Any]) -> Any:
    """Zwraca wartość FIA Grade z normalized.specs.fia_grade (lub None)."""
    if not normalized:
        return None
    specs = normalized.get("specs") or {}
    return specs.get("fia_grade")


def extract_history_events(normalized: dict[str, Any]) -> Any:
    """Zwraca listę zdarzeń z normalized.history.events (lub None)."""
    if not normalized:
        return None
    history_norm = normalized.get("history") or {}
    return history_norm.get("events")


def extract_infobox_layouts(infobox: dict[str, Any]) -> list[dict[str, Any]]:
    """Pobiera layouts z infobox."""
    if not infobox:
        return []

    layouts = infobox.get("layouts") or []

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
