from typing import TypedDict

from validation.schemas import RecordSchema


class CircuitBaseRecord(TypedDict, total=False):
    """Base envelope shared by circuit record variants (technical metadata only)."""

    url: str | None


CIRCUIT_BASE_SCHEMA = RecordSchema(
    types={"url": str},
    allow_none=("url",),
)
