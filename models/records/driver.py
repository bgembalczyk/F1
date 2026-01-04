from typing import Any, Optional, TypedDict

from models.records.driver_championships import DRIVERS_CHAMPIONSHIPS_SCHEMA
from models.records.driver_championships import DriversChampionshipsRecord
from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.records import NestedSchema
from validation.records import RecordSchema
from validation.records import RecordValidator


class DriverRecord(TypedDict, total=False):
    driver: LinkRecord
    is_active: bool
    is_world_champion: bool
    nationality: Optional[str]
    seasons_competed: list[SeasonRecord]
    drivers_championships: DriversChampionshipsRecord
    race_entries: Optional[int]
    race_starts: Optional[int]
    pole_positions: Optional[int]
    race_wins: Optional[int]
    podiums: Optional[int]
    fastest_laps: Optional[int]
    points: Optional[str]


DRIVER_SCHEMA = RecordSchema(
    required=(
        "driver",
        "nationality",
        "seasons_competed",
        "drivers_championships",
        "is_active",
        "is_world_champion",
    ),
    types={
        "driver": dict,
        "nationality": str,
        "seasons_competed": list,
        "drivers_championships": dict,
        "is_active": bool,
        "is_world_champion": bool,
    },
    nested={
        "driver": NestedSchema(LINK_SCHEMA),
        "seasons_competed": NestedSchema(SEASON_SCHEMA, is_list=True),
        "drivers_championships": NestedSchema(DRIVERS_CHAMPIONSHIPS_SCHEMA),
    },
)


def validate_driver_record(record: dict[str, Any]) -> list[str]:
    return RecordValidator.validate_schema(record, DRIVER_SCHEMA)
