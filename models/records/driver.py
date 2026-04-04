from typing_extensions import NotRequired
from typing_extensions import TypedDict

from models.records.driver_championships import DRIVERS_CHAMPIONSHIPS_SCHEMA
from models.records.driver_championships import DriversChampionshipsRecord
from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.record_definition import RecordDefinition
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.record_validation import validate_record
from validation.schemas import NestedSchema


class DriverRecord(TypedDict):
    driver: LinkRecord
    is_active: bool
    is_world_champion: bool
    nationality: str | None
    seasons_competed: list[SeasonRecord]
    drivers_championships: DriversChampionshipsRecord
    race_entries: NotRequired[int | None]
    race_starts: NotRequired[int | None]
    pole_positions: NotRequired[int | None]
    race_wins: NotRequired[int | None]
    podiums: NotRequired[int | None]
    fastest_laps: NotRequired[int | None]
    points: NotRequired[str | None]


DRIVER_DEFINITION = RecordDefinition(
    name="driver",
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

DRIVER_SCHEMA = DRIVER_DEFINITION.to_schema()


def validate_driver_record(record: dict[str, object]) -> list[str]:
    return [error.message for error in validate_record(record, DRIVER_SCHEMA)]
