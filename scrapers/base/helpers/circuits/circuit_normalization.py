"""Normalizacja rekordów torów - główna logika (z opcjonalną delegacją do CircuitService)."""

from __future__ import annotations

from typing import Any

from scrapers.base.helpers.time import normalize_date_value, normalize_time_value

from models.services.circuit_service import CircuitService  # type: ignore
from models.services.circuits.normalization import (
    normalize_circuit_record_impl,
)


def _normalize_circuit_record_local(raw: dict[str, Any]) -> dict[str, Any]:
    """Fallback do wspólnej implementacji normalizacji (gdy CircuitService nie istnieje)."""

    def normalize_lap_record(rec: Any) -> None:
        """Konwertuj na dict i normalizuj czas/daty (in-place)."""
        # Wspiera LapRecord, ale musimy pracować z dict dla normalize_time_value/normalize_date_value
        rec_dict = (
            rec
            if isinstance(rec, dict)
            else (rec.to_dict() if hasattr(rec, "to_dict") else rec)
        )
        if isinstance(rec_dict, dict):
            normalize_time_value(rec_dict)
            normalize_date_value(rec_dict)

    return normalize_circuit_record_impl(
        raw,
        normalize_lap_records_fn=normalize_lap_record,
    )


def normalize_circuit_record(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Normalizuje pojedynczy rekord toru wg ustalonych zasad.
    Jeśli istnieje CircuitService – deleguje; w przeciwnym razie używa fallbacku.
    """
    if CircuitService is not None:
        return CircuitService.normalize_record(raw)
    return _normalize_circuit_record_local(raw)
