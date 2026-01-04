from typing import TypedDict

from validation.records import RecordSchema


class CircuitBaseRecord(TypedDict, total=False):
    url: str | None


CIRCUIT_BASE_SCHEMA = RecordSchema(
    types={"url": str},
    allow_none=("url",),
)
