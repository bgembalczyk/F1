from typing import Any

from models.records.circuit_base import CircuitBaseRecord
from validation.validator_base import RecordValidator
from validation.schemas import RecordSchema


class CircuitDetailsRecord(CircuitBaseRecord):
    url: str
    infobox: dict[str, Any]
    tables: list[dict[str, Any]]


_CIRCUIT_DETAILS_SCHEMA = RecordSchema(
    required=("url", "infobox", "tables"),
    types={"url": str, "infobox": dict, "tables": list},
)


def validate_circuit_details_record(record: dict[str, object]) -> list[str]:
    return [
        error.message
        for error in RecordValidator.validate_schema(record, _CIRCUIT_DETAILS_SCHEMA)
    ]
