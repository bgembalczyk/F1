"""Delegacja kluczy rekordów do CircuitService."""

from __future__ import annotations

from typing import Any

from models.services.circuit_service import CircuitService


def extract_year_from_event(rec: dict[str, Any]) -> str | None:
    return CircuitService.extract_year_from_event(rec)


def record_key(rec: dict[str, Any]) -> tuple | None:
    return CircuitService.record_key(rec)


def core_key(rec: dict[str, Any]) -> tuple | None:
    return CircuitService.core_key(rec)
