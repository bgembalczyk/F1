from typing import Any
from typing import Literal
from typing import TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.record_definition import RecordDefinition
from models.records.record_definition import build_validator
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.issue import ValidationIssue
from validation.schemas import NestedSchema


class EngineManufacturerRecord(TypedDict, total=False):
    manufacturer: LinkRecord
    manufacturer_status: Literal["current", "former"]
    engines_built_in: list[LinkRecord]
    seasons: list[SeasonRecord]
    races_entered: int | None
    races_started: int | None
    wins: int | None
    points: float | None
    poles: int | None
    fastest_laps: int | None
    podiums: int | None
    wcc: int | None
    wdc: int | None


ENGINE_MANUFACTURER_DEFINITION = RecordDefinition(
    name="engine_manufacturer",
    required=("manufacturer", "manufacturer_status"),
    types={
        "manufacturer": dict,
        "manufacturer_status": str,
        "engines_built_in": list,
        "seasons": list,
    },
    nested={
        "manufacturer": NestedSchema(LINK_SCHEMA),
        "engines_built_in": NestedSchema(LINK_SCHEMA, is_list=True),
        "seasons": NestedSchema(SEASON_SCHEMA, is_list=True),
    },
)

ENGINE_MANUFACTURER_SCHEMA = ENGINE_MANUFACTURER_DEFINITION.to_schema()
_ENGINE_MANUFACTURER_VALIDATOR = build_validator(ENGINE_MANUFACTURER_DEFINITION)


def validate_engine_manufacturer_record(
    record: dict[str, Any],
) -> list[ValidationIssue]:
    return _ENGINE_MANUFACTURER_VALIDATOR(record)
