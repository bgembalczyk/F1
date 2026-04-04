from typing import Literal
from typing import TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.record_definition import RecordDefinition
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.schemas import NestedSchema
from validation.validator_base import RecordValidator


class CircuitRecord(TypedDict):
    circuit: LinkRecord
    circuit_status: Literal["current", "future", "former"]
    type: str | None
    direction: str | None
    location: str | None
    country: str | None
    last_length_used_km: float | None
    last_length_used_mi: float | None
    turns: int | None
    grands_prix: list[LinkRecord]
    seasons: list[SeasonRecord]
    grands_prix_held: int | None


CIRCUIT_DEFINITION = RecordDefinition(
    name="circuit",
    required=("circuit", "circuit_status", "country", "seasons"),
    types={
        "circuit": dict,
        "circuit_status": str,
        "country": (str, dict),
        "seasons": list,
        "grands_prix": list,
    },
    allow_none=("grands_prix",),
    nested={
        "circuit": NestedSchema(LINK_SCHEMA),
        "grands_prix": NestedSchema(LINK_SCHEMA, is_list=True),
        "seasons": NestedSchema(SEASON_SCHEMA, is_list=True),
    },
)

CIRCUIT_SCHEMA = CIRCUIT_DEFINITION.to_schema()


def validate_circuit_record(record: dict[str, object]) -> list[str]:
    return [
        error.message
        for error in RecordValidator.validate_schema(record, CIRCUIT_SCHEMA)
    ]
