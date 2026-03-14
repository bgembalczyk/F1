from typing import Any
from typing import TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.domain_validator import BaseDomainRecordValidator
from validation.issue import ValidationIssue
from validation.schemas import NestedSchema
from validation.schemas import RecordSchema


class ConstructorRecord(TypedDict, total=False):
    constructor: LinkRecord
    engine: list[LinkRecord]
    licensed_in: str | LinkRecord | list[LinkRecord] | None
    based_in: list[LinkRecord]
    team: str
    team_url: str | None
    seasons: list[SeasonRecord]
    races_entered: int | None
    races_started: int | None
    drivers: int | None
    total_entries: int | None
    wins: int | None
    points: int | None
    poles: int | None
    fastest_laps: int | None
    podiums: int | None
    wcc_titles: int | None
    wdc_titles: int | None
    antecedent_teams: list[LinkRecord]


CONSTRUCTOR_SCHEMA = RecordSchema(
    required=("constructor", "engine", "based_in", "seasons", "antecedent_teams"),
    types={
        "constructor": dict,
        "engine": list,
        "based_in": list,
        "seasons": list,
        "antecedent_teams": list,
    },
    nested={
        "constructor": NestedSchema(LINK_SCHEMA),
        "engine": NestedSchema(LINK_SCHEMA, is_list=True),
        "based_in": NestedSchema(LINK_SCHEMA, is_list=True),
        "seasons": NestedSchema(SEASON_SCHEMA, is_list=True),
        "antecedent_teams": NestedSchema(LINK_SCHEMA, is_list=True),
    },
)


def validate_constructor_record(record: dict[str, Any]) -> list[ValidationIssue]:
    return BaseDomainRecordValidator.validate_schema(record, CONSTRUCTOR_SCHEMA)
