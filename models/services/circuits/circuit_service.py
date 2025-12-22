"""Serwis domenowy dla torów wyścigowych."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scrapers.base.helpers.time import normalize_time_value, normalize_date_value

from models.services.circuits.normalization import (
    normalize_circuit_record_impl,
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

        def normalize_lap_record(rec: dict[str, Any]) -> None:
            """Normalizuj czas/daty w rekordzie okrążenia (in-place)."""
            normalize_time_value(rec)
            normalize_date_value(rec)

        return normalize_circuit_record_impl(
            raw,
            normalize_lap_records_fn=normalize_lap_record,
        )
