from typing import Any, TypedDict

from models.records.link import LinkRecord
from models.records.season import SeasonRecord
from validation.records import BaseDomainRecordValidator, ValidationIssue


class GrandsPrixRecord(TypedDict, total=False):
    race_title: LinkRecord
    race_status: str
    years_held: list[SeasonRecord]
    country: list[LinkRecord]
    circuits: int | None
    total: int | None


def validate_grands_prix_record(record: dict[str, Any]) -> list[ValidationIssue]:
    errors: list[ValidationIssue] = []
    errors.extend(
        BaseDomainRecordValidator.require_keys(
            record,
            ["race_title", "race_status", "years_held", "country", "total"],
        )
    )
    errors.extend(BaseDomainRecordValidator.require_type(record, "race_title", dict))
    errors.extend(BaseDomainRecordValidator.require_type(record, "race_status", str))
    errors.extend(BaseDomainRecordValidator.require_type(record, "years_held", list))
    errors.extend(BaseDomainRecordValidator.require_type(record, "country", list))
    errors.extend(
        BaseDomainRecordValidator.require_type(record, "total", int, allow_none=True)
    )
    errors.extend(
        BaseDomainRecordValidator.require_type(record, "circuits", int, allow_none=True)
    )

    race_title = record.get("race_title")
    if isinstance(race_title, dict):
        errors.extend(
            BaseDomainRecordValidator.require_link_dict(race_title, "race_title")
        )

    country = record.get("country")
    if isinstance(country, list):
        errors.extend(BaseDomainRecordValidator.require_link_list(country, "country"))

    return errors
