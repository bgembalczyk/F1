from typing import Any, TypedDict

from models.records.link import LinkRecord
from validation.records import BaseDomainRecordValidator, ValidationIssue


class SeasonSummaryRecord(TypedDict, total=False):
    season: LinkRecord
    races: int | None
    countries: int | None
    first: LinkRecord | None
    last: LinkRecord | None
    drivers_champion_team: list[LinkRecord]
    constructors_champion: list[LinkRecord]
    winners: int | None


def validate_season_summary_record(
    record: dict[str, Any]
) -> list[ValidationIssue]:
    errors: list[ValidationIssue] = []
    errors.extend(
        BaseDomainRecordValidator.require_keys(
            record,
            ["season", "races", "countries", "drivers_champion_team"],
        )
    )
    errors.extend(BaseDomainRecordValidator.require_type(record, "season", dict))
    errors.extend(
        BaseDomainRecordValidator.require_type(record, "races", int, allow_none=True)
    )
    errors.extend(
        BaseDomainRecordValidator.require_type(record, "countries", int, allow_none=True)
    )
    errors.extend(
        BaseDomainRecordValidator.require_type(
            record,
            "drivers_champion_team",
            list,
        )
    )
    errors.extend(
        BaseDomainRecordValidator.require_type(
            record,
            "constructors_champion",
            list,
            allow_none=True,
        )
    )
    errors.extend(
        BaseDomainRecordValidator.require_type(record, "winners", int, allow_none=True)
    )

    season = record.get("season")
    if isinstance(season, dict):
        errors.extend(BaseDomainRecordValidator.require_link_dict(season, "season"))

    drivers = record.get("drivers_champion_team")
    if isinstance(drivers, list):
        errors.extend(
            BaseDomainRecordValidator.require_link_list(drivers, "drivers_champion_team")
        )

    constructors = record.get("constructors_champion")
    if isinstance(constructors, list):
        errors.extend(
            BaseDomainRecordValidator.require_link_list(
                constructors,
                "constructors_champion",
            )
        )

    first = record.get("first")
    if isinstance(first, dict):
        errors.extend(BaseDomainRecordValidator.require_link_dict(first, "first"))

    last = record.get("last")
    if isinstance(last, dict):
        errors.extend(BaseDomainRecordValidator.require_link_dict(last, "last"))

    return errors
