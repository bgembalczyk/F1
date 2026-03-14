from typing import Any
from typing import Literal
from typing import TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.records import BaseDomainRecordValidator
from validation.records import NestedSchema
from validation.records import RecordSchema
from validation.records import ValidationIssue


class CircuitRecord(TypedDict, total=False):
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


CIRCUIT_SCHEMA = RecordSchema(
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


def validate_circuit_record(record: dict[str, Any]) -> list[ValidationIssue]:
    return BaseDomainRecordValidator.validate_schema(record, CIRCUIT_SCHEMA)
