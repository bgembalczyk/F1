from typing import Any

from models.records.circuit.base import CircuitBaseRecord
from validation.record_validation import validate_record
from validation.schemas import RecordSchema


class CircuitDetailsRecord(CircuitBaseRecord):
    infobox: dict[str, Any]
    tables: list[dict[str, Any]]


CIRCUIT_DETAILS_SCHEMA = RecordSchema(
    required=("url", "infobox", "tables"),
    types={"url": str, "infobox": dict, "tables": list},
)


def validate_circuit_details_record(record: dict[str, object]) -> list[str]:
    return [error.message for error in validate_record(record, CIRCUIT_DETAILS_SCHEMA)]
