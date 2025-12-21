"""Delegacja scalania rekordów do CircuitService."""

from __future__ import annotations

from models.services.circuit_service import CircuitService


def merge_race_lap_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return CircuitService.merge_race_lap_records(records)
