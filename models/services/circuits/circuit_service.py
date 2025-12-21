"""Serwis domenowy dla torów wyścigowych."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scrapers.base.helpers.time import normalize_time_value, normalize_date_value

from models.services.circuits.normalization import (
    extract_circuit_names,
    extract_circuit_url,
    extract_circuit_location,
    extract_circuit_grade_and_history,
    extract_infobox_layouts,
    merge_tables_into_layouts,
    cleanup_urls,
    remove_empty_lists,
)
from models.services.circuits.lap_record_merging import (
    merge_race_lap_records,
    build_record_key,
    build_core_key,
)


@dataclass(frozen=True)
class CircuitService:
    """Serwis domenowy dla operacji na torach wyścigowych."""

    @staticmethod
    def normalize_record(raw: dict[str, Any]) -> dict[str, Any]:
        """
        Normalizuje pojedynczy rekord toru wg ustalonych zasad:

        - circuit[text] -> name.list (dodajemy też infobox.title i infobox.normalized.name)
        - circuit[url] -> url, ale jeśli details == None -> url = None
        - former_names -> name.former_names
        - layouts z infobox.layouts przenosimy na wierzch, race_lap_record -> race_lap_records (lista)
        - tables łączymy z layouts (lap_records -> race_lap_records odpowiedniego layoutu)
        - location: { places, coordinates }
        - fia_grade wyciągnięte na wierzch
        - history: tylko lista events
        - nie kopiujemy last_length_used_km, last_length_used_mi, turns, specs (poza fia_grade)
        """
        out: dict[str, Any] = {}

        details = raw.get("details")

        infobox = None
        normalized = None
        if isinstance(details, dict):
            infobox = (details or {}).get("infobox") or {}
            normalized = infobox.get("normalized") or {}

        # name + url
        out["name"] = extract_circuit_names(raw, infobox, normalized)
        out["url"] = extract_circuit_url(raw, details)

        # proste pola z wierzchu
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

        # location
        out["location"] = extract_circuit_location(raw, normalized)

        # fia_grade + history (events)
        fia_grade, history_events = extract_circuit_grade_and_history(normalized)
        if fia_grade is not None:
            out["fia_grade"] = fia_grade
        if history_events is not None:
            out["history"] = history_events

        # layouts
        layouts = extract_infobox_layouts(infobox)

        # tables łączymy z layouts
        tables = None
        if isinstance(details, dict):
            tables = details.get("tables")
        tables = tables or []

        merge_tables_into_layouts(tables, layouts)

        if layouts:
            out["layouts"] = layouts

        # Apply cleanup to layout records
        for lay in out.get("layouts", []):
            records = lay.get("race_lap_records", [])
            for r in records:
                normalize_time_value(r)
                normalize_date_value(r)

        # Clean url=None in whole output
        out = cleanup_urls(out)
        out = remove_empty_lists(out)

        return out

    @staticmethod
    def merge_race_lap_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Łączy duplikujące się rekordy okrążeń (infobox + tabela) w jeden bogaty rekord.

        Deleguje do modułu lap_record_merging.
        """
        return merge_race_lap_records(records)

    @staticmethod
    def record_key(rec: dict[str, Any]) -> tuple | None:
        """Zwraca klucz rekordu dla identyfikacji duplikatów."""
        return build_record_key(rec)

    @staticmethod
    def core_key(rec: dict[str, Any]) -> tuple | None:
        """Zwraca klucz rdzeniowy (bez czasu) dla identyfikacji duplikatów."""
        return build_core_key(rec)
