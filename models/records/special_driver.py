from typing import Any, TypedDict

from models.records.link import LinkRecord
from models.records.season import SeasonRecord
from validation.records import RecordValidator


class SpecialDriverRecord(TypedDict, total=False):
    driver: LinkRecord
    seasons: list[SeasonRecord]
    teams: list[LinkRecord]
    entries: int | None
    starts: int | None
    points: float | dict[str, float] | None


def validate_special_driver_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(
        RecordValidator.require_keys(record, ["driver", "seasons", "teams"])
    )
    errors.extend(RecordValidator.require_type(record, "driver", dict))
    errors.extend(RecordValidator.require_type(record, "seasons", list))
    errors.extend(RecordValidator.require_type(record, "teams", list))
    errors.extend(RecordValidator.require_type(record, "entries", int, allow_none=True))
    errors.extend(RecordValidator.require_type(record, "starts", int, allow_none=True))

    driver = record.get("driver")
    if isinstance(driver, dict):
        errors.extend(RecordValidator.require_link_dict(driver, "driver"))

    teams = record.get("teams")
    if isinstance(teams, list):
        errors.extend(RecordValidator.require_link_list(teams, "teams"))

    return errors
