from typing import TypedDict

from models.records.record_definition import RecordDefinition
from models.records.schema_fragments import compose_schema_fragments
from validation.record_validation import validate_record
from validation.schemas import NestedSchema


class ConstructorSummaryRecord(TypedDict, total=False):
    constructor: dict[str, str | None]
    engine: list[dict[str, str | None]]
    licensed_in: str | dict[str, str | None] | list[dict[str, str | None]] | None
    based_in: list[dict[str, str | None]]
    team: str
    team_url: str | None
    seasons: list[dict[str, int | str]]
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
    antecedent_teams: list[dict[str, str | None]]


ConstructorRecord = ConstructorSummaryRecord

_constructor_link = compose_schema_fragments("link")["nested"]["link"]
_constructor_seasons = compose_schema_fragments("seasons")["nested"]["seasons"]

CONSTRUCTOR_SUMMARY_DEFINITION = RecordDefinition(
    name="constructor_summary",
    required=("constructor", "engine", "based_in", "seasons", "antecedent_teams"),
    types={
        "constructor": dict,
        "engine": list,
        "based_in": list,
        "seasons": list,
        "antecedent_teams": list,
    },
    nested={
        "constructor": _constructor_link,
        "engine": NestedSchema(_constructor_link.schema, is_list=True),
        "based_in": NestedSchema(_constructor_link.schema, is_list=True),
        "seasons": _constructor_seasons,
        "antecedent_teams": NestedSchema(_constructor_link.schema, is_list=True),
    },
)

CONSTRUCTOR_SCHEMA = CONSTRUCTOR_SUMMARY_DEFINITION.to_schema()


def validate_constructor_record(record: dict[str, object]) -> list[str]:
    return [error.message for error in validate_record(record, CONSTRUCTOR_SCHEMA)]
