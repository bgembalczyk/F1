from typing import Any

from models.records.circuit_base import CircuitBaseRecord
from models.records.link import LinkRecord
from models.records.season import SeasonRecord


class CircuitCompleteRecord(CircuitBaseRecord, total=False):
    name: dict[str, Any]
    circuit_status: str
    type: str | None
    direction: str | None
    grands_prix: list[LinkRecord]
    seasons: list[SeasonRecord]
    grands_prix_held: int | None
    location: dict[str, Any]
    fia_grade: str
    history: list[Any]
    layouts: list[dict[str, Any]]


def validate_circuit_complete_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if "url" in record and record.get("url") is not None and not isinstance(
        record.get("url"),
        str,
    ):
        errors.append("Invalid type for url: expected str or None")
    return errors
