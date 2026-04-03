"""Serwis domenowy dla torów wyścigowych."""

from dataclasses import dataclass
from typing import Any

from models.services import normalize_date_value
from models.services import prune_empty
from scrapers.circuits.models.services.constants import TOP_LEVEL_KEYS
from scrapers.circuits.models.services.lap_record_merging import merge_race_lap_records
from scrapers.circuits.models.services.lap_record_merging import normalize_lap_record
from scrapers.circuits.models.services.normalization import extract_circuit_location
from scrapers.circuits.models.services.normalization import extract_circuit_names
from scrapers.circuits.models.services.normalization import extract_circuit_url
from scrapers.circuits.models.services.normalization import extract_fia_grade
from scrapers.circuits.models.services.normalization import extract_history_events
from scrapers.circuits.models.services.normalization import extract_infobox_layouts
from scrapers.circuits.models.services.normalization import merge_tables_into_layouts


@dataclass(frozen=True)
class CircuitService:
    """Serwis domenowy dla operacji na torach wyścigowych."""

    @staticmethod
    def _extract_infobox_data(details: Any) -> tuple[dict[str, Any], dict[str, Any]]:
        if not isinstance(details, dict):
            return {}, {}
        infobox = details.get("infobox") or {}
        return infobox, infobox.get("normalized") or {}

    @staticmethod
    def _copy_top_level_fields(raw: dict[str, Any], out: dict[str, Any]) -> None:
        for key in TOP_LEVEL_KEYS:
            if key in raw:
                out[key] = raw[key]

    @staticmethod
    def _normalize_layout_lap_records(out: dict[str, Any]) -> None:
        for lay in out.get("layouts", []):
            records = lay.get("race_lap_records", []) or []
            for rec in records:
                normalize_lap_record(rec)
                normalize_date_value(rec)
            if records:
                lay["race_lap_records"] = merge_race_lap_records(records)

    @staticmethod
    def normalize_record(raw: dict[str, Any]) -> dict[str, Any]:
        """Normalizuje pojedynczy rekord toru wg ustalonych zasad."""
        out: dict[str, Any] = {}
        details = raw.get("details")
        infobox, normalized = CircuitService._extract_infobox_data(details)

        out["name"] = extract_circuit_names(raw, infobox, normalized)
        out["url"] = extract_circuit_url(raw, details)
        CircuitService._copy_top_level_fields(raw, out)
        out["location"] = extract_circuit_location(raw, normalized)

        fia_grade = extract_fia_grade(normalized)
        history_events = extract_history_events(normalized)
        if fia_grade is not None:
            out["fia_grade"] = fia_grade
        if history_events is not None:
            out["history"] = history_events

        layouts = extract_infobox_layouts(infobox)
        tables = (details.get("tables") if isinstance(details, dict) else None) or []
        merge_tables_into_layouts(tables, layouts)

        if layouts:
            out["layouts"] = layouts
            CircuitService._normalize_layout_lap_records(out)

        return prune_empty(
            out,
            drop_empty_lists=True,
            drop_none=False,
            drop_empty_dicts=False,
            drop_url_none=True,
        )
