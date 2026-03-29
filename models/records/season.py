from typing import TypedDict

from validation.schemas import RecordSchema

SEASON_SCHEMA = RecordSchema(
    required=("year", "url"),
    types={"year": int, "url": str},
)


class SeasonRecord(TypedDict):
    year: int
    url: str
