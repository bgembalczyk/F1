from typing import TypedDict

from models.records.car import CAR_SCHEMA
from models.records.car import CarRecord
from models.records.event import EVENT_SCHEMA
from models.records.event import EventRecord
from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from validation.schemas import NestedSchema
from validation.schemas import RecordSchema


class FatalityRecord(TypedDict, total=False):
    driver: LinkRecord
    date: str | None
    age: int | None
    event: EventRecord | None
    circuit: LinkRecord | None
    car: CarRecord | None
    session: str | None


FATALITY_SCHEMA = RecordSchema(
    types={"date": str, "age": int, "session": str},
    allow_none=("date", "age", "session"),
    nested={
        "driver": NestedSchema(LINK_SCHEMA),
        "event": NestedSchema(EVENT_SCHEMA),
        "circuit": NestedSchema(LINK_SCHEMA),
        "car": NestedSchema(CAR_SCHEMA),
    },
)
