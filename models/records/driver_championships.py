from typing import TypedDict

from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.schemas import NestedSchema
from validation.schemas import RecordSchema

DRIVERS_CHAMPIONSHIPS_SCHEMA = RecordSchema(
    required=("count", "seasons"),
    types={"count": int, "seasons": list},
    nested={"seasons": NestedSchema(SEASON_SCHEMA, is_list=True)},
)


class DriversChampionshipsRecord(TypedDict):
    count: int
    seasons: list[SeasonRecord]
