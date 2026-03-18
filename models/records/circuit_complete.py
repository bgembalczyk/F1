from typing import Any

from models.records.circuit_base import CIRCUIT_BASE_SCHEMA
from models.records.circuit_base import CircuitBaseRecord
from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.validator_base import RecordValidator
from validation.issue import ValidationIssue
from validation.schemas import NestedSchema
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


CIRCUIT_COMPLETE_SCHEMA = RecordSchema(
    types={
        **CIRCUIT_BASE_SCHEMA.types,
        "name": dict,
        "circuit_status": str,
        "type": str,
        "direction": str,
        "grands_prix": list,
        "seasons": list,
        "grands_prix_held": int,
        "location": dict,
        "fia_grade": str,
        "history": list,
        "layouts": list,
    },
    allow_none=(
        *CIRCUIT_BASE_SCHEMA.allow_none,
        "name",
        "circuit_status",
        "type",
        "direction",
        "grands_prix",
        "seasons",
        "grands_prix_held",
        "location",
        "fia_grade",
        "history",
        "layouts",
    ),
    nested={
        "grands_prix": NestedSchema(LINK_SCHEMA, is_list=True),
        "seasons": NestedSchema(SEASON_SCHEMA, is_list=True),
    },
)


def validate_circuit_complete_record(record: dict[str, Any]) -> list[ValidationIssue]:
    return RecordValidator.validate_schema(record, CIRCUIT_COMPLETE_SCHEMA)
