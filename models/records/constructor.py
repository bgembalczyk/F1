from typing import Any, Optional, TypedDict


from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.records import NestedSchema
from validation.records import RecordSchema
from validation.records import BaseDomainRecordValidator


class ConstructorRecord(TypedDict, total=False):
    constructor: LinkRecord
    engine: list[LinkRecord]
    licensed_in: Optional[str | LinkRecord | list[LinkRecord]]
    based_in: list[LinkRecord]
    team: str
    team_url: Optional[str]
    seasons: list[SeasonRecord]
    races_entered: Optional[int]
    races_started: Optional[int]
    drivers: Optional[int]
    total_entries: Optional[int]
    wins: Optional[int]
    points: Optional[int]
    poles: Optional[int]
    fastest_laps: Optional[int]
    podiums: Optional[int]
    wcc_titles: Optional[int]
    wdc_titles: Optional[int]
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


def validate_constructor_record(record: dict[str, Any]) -> list[str]:
    return BaseDomainRecordValidator.validate_schema(record, CONSTRUCTOR_SCHEMA)
