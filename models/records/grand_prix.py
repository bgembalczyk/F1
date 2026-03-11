from typing import Any, TypedDict

from models.records.link import LinkRecord
from models.records.season import SeasonRecord
from validation.records import ValidationIssue


class GrandsPrixRecord(TypedDict, total=False):
    race_title: LinkRecord
    race_status: str
    years_held: list[SeasonRecord]
    country: list[LinkRecord]
    circuits: int | None
    total: int | None


def validate_grands_prix_record(record: dict[str, Any]) -> list[ValidationIssue]:
    """
    Validates a grands prix record.
    
    This function is a convenience wrapper that delegates to GrandsPrixRecordValidator.
    It's kept for backward compatibility but new code should use the validator directly.
    """
    # Import here to avoid circular dependency
    from scrapers.grands_prix.validator import GrandsPrixRecordValidator

    validator = GrandsPrixRecordValidator()
    return validator.validate(record)
