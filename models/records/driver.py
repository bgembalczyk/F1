from typing_extensions import NotRequired
from typing_extensions import TypedDict

from models.records.driver_championships import DRIVERS_CHAMPIONSHIPS_SCHEMA
from models.records.driver_championships import DriversChampionshipsRecord
from models.records.record_definition import RecordDefinition
from models.records.schema_fragments import compose_schema_fragments
from validation.record_validation import validate_record
from validation.schemas import NestedSchema


class DriverSummaryRecord(TypedDict):
    driver: dict[str, str | None]
    is_active: bool
    is_world_champion: bool
    nationality: str | None
    seasons_competed: list[dict[str, int | str]]
    drivers_championships: DriversChampionshipsRecord
    race_entries: NotRequired[int | None]
    race_starts: NotRequired[int | None]
    pole_positions: NotRequired[int | None]
    race_wins: NotRequired[int | None]
    podiums: NotRequired[int | None]
    fastest_laps: NotRequired[int | None]
    points: NotRequired[str | None]


DriverRecord = DriverSummaryRecord

_driver_common_fragments = compose_schema_fragments("link")

DRIVER_SUMMARY_DEFINITION = RecordDefinition(
    name="driver_summary",
    required=(
        "driver",
        "nationality",
        "seasons_competed",
        "drivers_championships",
        "is_active",
        "is_world_champion",
    ),
    types={
        **_driver_common_fragments["types"],
        "nationality": str,
        "seasons_competed": list,
        "drivers_championships": dict,
        "is_active": bool,
        "is_world_champion": bool,
    },
    nested={
        "driver": _driver_common_fragments["nested"]["link"],
        "seasons_competed": NestedSchema(
            schema=compose_schema_fragments("seasons")["nested"]["seasons"].schema,
            is_list=True,
        ),
        "drivers_championships": NestedSchema(DRIVERS_CHAMPIONSHIPS_SCHEMA),
    },
)

DRIVER_SCHEMA = DRIVER_SUMMARY_DEFINITION.to_schema()


def validate_driver_record(record: dict[str, object]) -> list[str]:
    return [error.message for error in validate_record(record, DRIVER_SCHEMA)]
