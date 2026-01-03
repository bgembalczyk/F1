from typing import Any, Optional, TypedDict


from models.records.link import LinkRecord
from models.records.season import SeasonRecord
from validation.records import RecordValidator


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


def validate_constructor_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(
        RecordValidator.require_keys(
            record,
            ["constructor", "engine", "based_in", "seasons", "antecedent_teams"],
        )
    )
    errors.extend(RecordValidator.require_type(record, "constructor", dict))
    errors.extend(RecordValidator.require_type(record, "engine", list))
    errors.extend(RecordValidator.require_type(record, "based_in", list))
    errors.extend(RecordValidator.require_type(record, "seasons", list))
    errors.extend(RecordValidator.require_type(record, "antecedent_teams", list))

    constructor = record.get("constructor")
    if isinstance(constructor, dict):
        errors.extend(RecordValidator.require_link_dict(constructor, "constructor"))

    engine = record.get("engine")
    if isinstance(engine, list):
        errors.extend(RecordValidator.require_link_list(engine, "engine"))

    based_in = record.get("based_in")
    if isinstance(based_in, list):
        errors.extend(RecordValidator.require_link_list(based_in, "based_in"))

    antecedent_teams = record.get("antecedent_teams")
    if isinstance(antecedent_teams, list):
        errors.extend(
            RecordValidator.require_link_list(antecedent_teams, "antecedent_teams")
        )

    return errors
