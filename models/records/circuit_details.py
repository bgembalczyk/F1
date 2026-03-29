from typing import Any

from models.records.circuit_base import CircuitBaseRecord


class CircuitDetailsRecord(CircuitBaseRecord):
    url: str
    infobox: dict[str, Any]
    tables: list[dict[str, Any]]


def validate_circuit_details_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("url") is None:
        errors.append("Null value for: url")
    if not isinstance(record.get("infobox"), dict):
        errors.append("Invalid type for infobox: expected dict")
    if not isinstance(record.get("tables"), list):
        errors.append("Invalid type for tables: expected list")
    return errors
