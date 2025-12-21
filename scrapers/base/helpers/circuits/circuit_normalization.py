"""Normalizacja rekordów torów - delegacja do usług domenowych."""

from __future__ import annotations

from typing import Any

from models.services.circuit_service import CircuitService


def normalize_circuit_record(raw: dict[str, Any]) -> dict[str, Any]:
    return CircuitService.normalize_record(raw)
