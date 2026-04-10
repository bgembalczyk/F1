from typing import TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.schemas import NestedSchema


class HasLinkRecord(TypedDict):
    link: LinkRecord


class HasSeasonsRecord(TypedDict):
    seasons: list[SeasonRecord]


class HasStatsRecord(TypedDict, total=False):
    stats: dict[str, int | float | str | None]


class HasStatusRecord(TypedDict):
    status: str


class HasLocationRecord(TypedDict, total=False):
    location: str | None


SHARED_SCHEMA_FRAGMENTS = {
    "link": {
        "types": {"link": dict},
        "nested": {"link": NestedSchema(LINK_SCHEMA)},
    },
    "seasons": {
        "types": {"seasons": list},
        "nested": {"seasons": NestedSchema(SEASON_SCHEMA, is_list=True)},
    },
    "stats": {
        "types": {"stats": dict},
    },
    "status": {
        "types": {"status": str},
    },
    "location": {
        "types": {"location": str},
        "allow_none": ("location",),
    },
}


__all__ = [
    "HasLinkRecord",
    "HasSeasonsRecord",
    "HasStatsRecord",
    "HasStatusRecord",
    "HasLocationRecord",
    "SHARED_SCHEMA_FRAGMENTS",
]
