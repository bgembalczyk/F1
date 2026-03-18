from typing import Any
from typing import TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.record_definition import RecordDefinition
from models.records.record_definition import build_validator
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.issue import ValidationIssue
from validation.schemas import NestedSchema


class GrandsPrixRecord(TypedDict, total=False):
    race_title: LinkRecord
    race_status: str
    years_held: list[SeasonRecord]
    country: list[LinkRecord]
    circuits: int | None
    total: int | None


GRANDS_PRIX_DEFINITION = RecordDefinition(
    name="grands_prix",
    required=("race_title", "race_status", "years_held", "country", "total"),
    types={
        "race_title": dict,
        "race_status": str,
        "years_held": list,
        "country": list,
        "circuits": int,
        "total": int,
    },
    allow_none=("circuits", "total"),
    nested={
        "race_title": NestedSchema(LINK_SCHEMA),
        "years_held": NestedSchema(SEASON_SCHEMA, is_list=True),
        "country": NestedSchema(LINK_SCHEMA, is_list=True),
    },
)

GRANDS_PRIX_SCHEMA = GRANDS_PRIX_DEFINITION.to_schema()
_GRANDS_PRIX_VALIDATOR = build_validator(GRANDS_PRIX_DEFINITION)


def validate_grands_prix_record(record: dict[str, Any]) -> list[ValidationIssue]:
    return _GRANDS_PRIX_VALIDATOR(record)
