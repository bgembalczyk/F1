"""Normalizacja rekordów torów - główna logika."""

from __future__ import annotations
from typing import Any
import re

from scrapers.base.helpers.record_merging import merge_race_lap_records
from scrapers.base.helpers.text_processing import add_name
from scrapers.base.helpers.time_processing import simplify_time, simplify_date


def extract_circuit_names(raw: dict[str, Any], infobox: dict[str, Any], normalized: dict[str, Any]) -> dict[str, Any]:
    """Ekstrakcja nazwy i poprzednich nazw toru."""
    circuit = raw.get("circuit") or {}
    name_set: set[str] = set()
    name_list: list[str] = []

    # 1) circuit[text] -> name.list
    add_name(name_set, name_list, circuit.get("text"))

    # 2) infobox.title + infobox.normalized.name
    if infobox:
        add_name(name_set, name_list, infobox.get("title"))
    if normalized:
        add_name(name_set, name_list, normalized.get("name"))

    # 3) former_names -> name.former_names
    former_names: list[dict[str, Any]] = []
    if normalized:
        history_norm = normalized.get("history") or {}
        former_names = history_norm.get("former_names") or []

    return {
        "list": name_list,
        "former_names": former_names,
    }


def extract_circuit_url(raw: dict[str, Any], details: dict[str, Any] | None) -> str | None:
    """Ekstrakcja URL toru (None jeśli brak szczegółów)."""
    circuit = raw.get("circuit") or {}
    if details is None:
        return None
    return circuit.get("url")


def extract_circuit_location(raw: dict[str, Any], normalized: dict[str, Any]) -> dict[str, Any]:
    """Ekstrakcja lokalizacji toru z konsolidacją miejsc i współrzędnych."""
    country = raw.get("country")
    old_location = raw.get("location")
    new_location = normalized.get("location") if normalized else None
    coordinates = normalized.get("coordinates") if normalized else None

    def extract_place(text: str | None, url: str | None) -> dict[str, Any] | None:
        if not text:
            return None
        clean = text.strip()
        if not clean:
            return None
        return {"text": clean, "url": url}

    places_map: dict[str, dict[str, Any]] = {}

    # 1) old_location → places
    if isinstance(old_location, dict):
        p = extract_place(old_location.get("text"), old_location.get("url"))
        if p:
            places_map[p["text"]] = p

    # 2) new_location → places
    if isinstance(new_location, dict):
        for _, val in new_location.items():
            if not isinstance(val, dict):
                continue
            text = val.get("text") or val.get("label")
            link = val.get("link") or {}
            url = link.get("url")
            p = extract_place(text, url)
            if p:
                places_map[p["text"]] = p

    # 3) country też trafia do places
    if country:
        p = extract_place(country, None)
        if p:
            places_map.setdefault(p["text"], p)

    return {
        "places": list(places_map.values()),
        "coordinates": coordinates,
    }


def extract_circuit_grade_and_history(normalized: dict[str, Any]) -> tuple[str | None, list[Any] | None]:
    """Ekstrakcja klasy FIA i historii zdarzeń."""
    if not normalized:
        return None, None

    specs = normalized.get("specs") or {}
    fia_grade = specs.get("fia_grade")

    history_norm = normalized.get("history") or {}
    history_events = history_norm.get("events")

    return fia_grade, history_events


def extract_infobox_layouts(infobox: dict[str, Any]) -> list[dict[str, Any]]:
    """Ekstrakcja layoutów z infoboxu i konwersja race_lap_record na listę."""
    layouts: list[dict[str, Any]] = []
    if not infobox:
        return layouts

    for layout in infobox.get("layouts") or []:
        lay = dict(layout)
        rlr = lay.pop("race_lap_record", None)
        records: list[dict[str, Any]] = []
        if rlr is not None:
            if isinstance(rlr, dict):
                records.append(rlr)
        lay["race_lap_records"] = records
        layouts.append(lay)

    return layouts


def parse_table_layout_info(table_layout: str) -> tuple[float | None, str | None]:
    """Parsuje informacje o długości i latach z tekstu layoutu tabeli."""
    length_km: float | None = None
    years_str: str | None = None

    # długość w km
    m_len = re.search(r"([\d.,]+)\s*km", table_layout)
    if m_len:
        length_km = float(m_len.group(1).replace(",", "."))

    # lata w nawiasie na końcu
    m_years = re.search(r"\(([^()]*)\)\s*$", table_layout)
    if m_years:
        years_str = m_years.group(1).strip().lower()

    return length_km, years_str


def find_layout_for_table(table_layout: str, layouts: list[dict[str, Any]]) -> dict[str, Any] | None:
    """
    Dopasowuje layout z tabeli do layoutu z infoboxa na podstawie:
    - długości okrążenia (km),
    - lat obowiązywania layoutu.
    """
    if not table_layout:
        return None

    length_km, years_str = parse_table_layout_info(table_layout)
    best_candidate: dict[str, Any] | None = None

    for lay in layouts:
        lay_len = lay.get("length_km")
        lay_years_raw = lay.get("years") or ""
        lay_years = lay_years_raw.strip().lower()

        # 1) dopasowanie długości
        if length_km is not None and lay_len is not None:
            if abs(lay_len - length_km) > 1e-3:
                continue

        # 2) dopasowanie lat
        if years_str and lay_years:
            if years_str == lay_years:
                return lay

            # bardziej miękka heurystyka: porównujemy rok startowy
            y_tab = re.search(r"\d{4}", years_str)
            y_lay = re.search(r"\d{4}", lay_years)
            if y_tab and y_lay and y_tab.group(0) != y_lay.group(0):
                continue

        # jeżeli przeszliśmy powyższe filtry – traktujemy jako kandydata
        if best_candidate is None:
            best_candidate = lay

    return best_candidate


def merge_tables_into_layouts(tables: list[dict[str, Any]], layouts: list[dict[str, Any]]) -> None:
    """Łączy rekordy z tabel w odpowiednie layouty."""
    for table_block in tables:
        t_layout_str = table_block.get("layout")
        lap_records = table_block.get("lap_records") or []
        if not t_layout_str:
            continue

        target_layout = find_layout_for_table(t_layout_str, layouts)
        if target_layout is None:
            layouts.append(
                {
                    "layout": t_layout_str,
                    "race_lap_records": list(lap_records),
                }
            )
        else:
            target_layout.setdefault("race_lap_records", [])
            target_layout["race_lap_records"].extend(lap_records)

    # deduplikacja i scalanie race_lap_records w ramach każdego layoutu
    for lay in layouts:
        records = lay.get("race_lap_records") or []
        if records:
            lay["race_lap_records"] = merge_race_lap_records(records)


def cleanup_urls(obj: Any) -> Any:
    """Usuwa url=None oraz rekursywnie czyści elementy."""
    if isinstance(obj, list):
        return [cleanup_urls(x) for x in obj if x is not None]

    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if v is None:
                continue
            cv = cleanup_urls(v)
            if cv == []:
                continue
            if isinstance(cv, dict) and set(cv.keys()) == set():
                continue
            cleaned[k] = cv
        return cleaned

    return obj


def remove_empty_lists(obj: Any) -> Any:
    """Rekursywnie usuwa puste listy ze struktury."""
    if isinstance(obj, dict):
        keys_to_del = []
        for k, v in obj.items():
            rv = remove_empty_lists(v)
            if rv == []:
                keys_to_del.append(k)
            else:
                obj[k] = rv
        for k in keys_to_del:
            del obj[k]
        return obj
    if isinstance(obj, list):
        new_list = [remove_empty_lists(x) for x in obj]
        return [x for x in new_list if x != []]
    return obj


def normalize_circuit_record(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Normalizuje pojedynczy rekord toru wg ustalonych zasad:

    - circuit[text] -> name.list (dodajemy też infobox.title i infobox.normalized.name)
    - circuit[url] -> url, ale jeśli details == None -> url = None
    - former_names -> name.former_names
    - layouts z infobox.layouts przenosimy na górę, race_lap_record -> race_lap_records (lista)
    - tables łączymy z layouts (lap_records -> race_lap_records odpowiedniego layoutu)
    - location: { places, coordinates }
    - fia_grade wyciągnięte na wierzch
    - history: tylko lista events
    - nie kopiujemy last_length_used_km, last_length_used_mi, turns, specs (poza fia_grade)
    """
    out: dict[str, Any] = {}

    circuit = raw.get("circuit") or {}
    details = raw.get("details")

    infobox = None
    normalized = None
    if isinstance(details, dict):
        infobox = (details or {}).get("infobox") or {}
        normalized = infobox.get("normalized") or {}

    # -----------------------
    # name + url
    # -----------------------
    out["name"] = extract_circuit_names(raw, infobox, normalized)
    out["url"] = extract_circuit_url(raw, details)

    # -----------------------
    # proste pola z wierzchu
    # -----------------------
    for key in (
        "circuit_status",
        "type",
        "direction",
        "grands_prix",
        "seasons",
        "grands_prix_held",
    ):
        if key in raw:
            out[key] = raw[key]

    # -----------------------
    # location
    # -----------------------
    out["location"] = extract_circuit_location(raw, normalized)

    # -----------------------
    # fia_grade + history (events)
    # -----------------------
    fia_grade, history_events = extract_circuit_grade_and_history(normalized)
    if fia_grade is not None:
        out["fia_grade"] = fia_grade
    if history_events is not None:
        out["history"] = history_events

    # -----------------------
    # layouts
    # -----------------------
    layouts = extract_infobox_layouts(infobox)

    # -----------------------
    # tables łączymy z layouts
    # -----------------------
    tables = None
    if isinstance(details, dict):
        tables = details.get("tables")
    tables = tables or []

    merge_tables_into_layouts(tables, layouts)

    if layouts:
        out["layouts"] = layouts

    # -----------------------
    # FINAL CLEANUP JSON
    # -----------------------

    # Apply cleanup to layout records
    for lay in out.get("layouts", []):
        records = lay.get("race_lap_records", [])
        for r in records:
            simplify_time(r)
            simplify_date(r)

    # Clean url=None in whole output
    out = cleanup_urls(out)

    # Remove empty lists
    out = remove_empty_lists(out)

    return out

