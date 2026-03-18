from typing import Any
from typing import TypedDict

from models.records.car import CAR_SCHEMA
from models.records.car import CarRecord
from models.records.event import EVENT_SCHEMA
from models.records.event import EventRecord
from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.record_definition import RecordDefinition
from models.records.record_definition import build_validator
from validation.issue import ValidationIssue
from validation.schemas import NestedSchema


class FatalityRecord(TypedDict, total=False):
    driver: LinkRecord
    date: str | None
    age: int | None
    event: EventRecord | None
    circuit: LinkRecord | None
    car: CarRecord | None
    session: str | None


FATALITY_DEFINITION = RecordDefinition(
    name="fatality",
    types={"date": str, "age": int, "session": str},
    allow_none=("date", "age", "session"),
    nested={
        "driver": NestedSchema(LINK_SCHEMA),
        "event": NestedSchema(EVENT_SCHEMA),
        "circuit": NestedSchema(LINK_SCHEMA),
        "car": NestedSchema(CAR_SCHEMA),
    },
)

FATALITY_SCHEMA = FATALITY_DEFINITION.to_schema()
_FATALITY_VALIDATOR = build_validator(FATALITY_DEFINITION)


def validate_fatality_record(record: dict[str, Any]) -> list[ValidationIssue]:
    return _FATALITY_VALIDATOR(record)
