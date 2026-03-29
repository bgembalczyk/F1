from typing import Any

from models.records.circuit_base import CircuitBaseRecord
from models.records.link import LinkRecord
from models.records.season import SeasonRecord
from validation.validator_base import RecordValidator
from validation.schemas import RecordSchema


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


_CIRCUIT_COMPLETE_SCHEMA = RecordSchema(
    required=(),
    types={"url": (str, type(None))},
)


def validate_circuit_complete_record(record: dict[str, object]) -> list[str]:
    return [
        error.message
        for error in RecordValidator.validate_schema(record, _CIRCUIT_COMPLETE_SCHEMA)
    ]
