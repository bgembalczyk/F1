from typing import Any, TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.records import NestedSchema
from validation.records import RecordSchema
from validation.records import RecordValidator


class CircuitCompleteRecord(TypedDict, total=False):
    name: dict[str, Any]
    url: str | None
    circuit_status: str
    type: str | None
    direction: str | None
    grands_prix: list[LinkRecord]
    seasons: list[SeasonRecord]
    grands_prix_held: int | None
    location: dict[str, Any]
    fia_grade: str
    history: list[Any]
    layouts: list[dict[str, Any]]


CIRCUIT_COMPLETE_SCHEMA = RecordSchema(
    types={
        "name": dict,
        "url": str,
        "circuit_status": str,
        "type": str,
        "direction": str,
        "grands_prix": list,
        "seasons": list,
        "grands_prix_held": int,
        "location": dict,
        "fia_grade": str,
        "history": list,
        "layouts": list,
    },
    allow_none=(
        "name",
        "url",
        "circuit_status",
        "type",
        "direction",
        "grands_prix",
        "seasons",
        "grands_prix_held",
        "location",
        "fia_grade",
        "history",
        "layouts",
    ),
    nested={
        "grands_prix": NestedSchema(LINK_SCHEMA, is_list=True),
        "seasons": NestedSchema(SEASON_SCHEMA, is_list=True),
    },
)


def validate_circuit_complete_record(record: dict[str, Any]) -> list[str]:
    return RecordValidator.validate_schema(record, CIRCUIT_COMPLETE_SCHEMA)
