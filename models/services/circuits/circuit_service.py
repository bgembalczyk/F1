"""Serwis domenowy dla torów wyścigowych."""

from dataclasses import dataclass
from typing import Any

from scrapers.base.helpers.time import normalize_time_value, normalize_date_value
from scrapers.base.helpers.prune import prune_empty

from models.services.circuits.normalization import (
    extract_circuit_names,
    extract_circuit_url,
    extract_circuit_location,
    extract_circuit_grade_and_history,
    extract_infobox_layouts,
    merge_tables_into_layouts,
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

        infobox: dict[str, Any] = {}
        normalized: dict[str, Any] = {}
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

        # Normalizacja rekordów okrążeń
        for lay in out.get("layouts", []):
            records = lay.get("race_lap_records", []) or []
            for rec in records:
                normalize_time_value(rec)
                normalize_date_value(rec)

        # Clean url=None w całym wyjściu
        out = prune_empty(
            out,
            drop_empty_lists=True,
            drop_none=False,
            drop_empty_dicts=False,
            drop_url_none=True,
        )

        return out

