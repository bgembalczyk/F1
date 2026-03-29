from typing import TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.schemas import NestedSchema
from validation.schemas import RecordSchema


class SpecialDriverRecord(TypedDict, total=False):
    driver: LinkRecord
    seasons: list[SeasonRecord]
    teams: list[LinkRecord]
    entries: int | None
    starts: int | None
    points: float | dict[str, float] | None


SPECIAL_DRIVER_SCHEMA = RecordSchema(
    required=("driver", "seasons", "teams"),
    types={
        "driver": dict,
        "seasons": list,
        "teams": list,
        "entries": int,
        "starts": int,
    },
    allow_none=("entries", "starts"),
    nested={
        "driver": NestedSchema(LINK_SCHEMA),
        "seasons": NestedSchema(SEASON_SCHEMA, is_list=True),
        "teams": NestedSchema(LINK_SCHEMA, is_list=True),
    },
)
