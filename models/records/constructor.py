from typing import TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.record_definition import RecordDefinition
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.record_validation import validate_record
from validation.schemas import NestedSchema


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


CONSTRUCTOR_DEFINITION = RecordDefinition(
    name="constructor",
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

CONSTRUCTOR_SCHEMA = CONSTRUCTOR_DEFINITION.to_schema()


def validate_constructor_record(record: dict[str, object]) -> list[str]:
    return [error.message for error in validate_record(record, CONSTRUCTOR_SCHEMA)]
