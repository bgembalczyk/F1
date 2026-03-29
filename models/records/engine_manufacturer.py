from typing import Literal
from typing import TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.schemas import NestedSchema
from validation.schemas import RecordSchema


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


ENGINE_MANUFACTURER_SCHEMA = RecordSchema(
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
