from typing import Optional, TypedDict

from models.records.link import LinkRecord


class CarRecord(LinkRecord, total=False):
    formula_category: str


class EventRecord(TypedDict, total=False):
    event: Optional[str | LinkRecord | list[LinkRecord]]
    championship: bool


class FatalityRecord(TypedDict, total=False):
    driver: LinkRecord
    date: Optional[str]
    age: Optional[int]
    event: Optional[EventRecord]
    circuit: Optional[LinkRecord]
    car: Optional[CarRecord]
    session: Optional[str]
