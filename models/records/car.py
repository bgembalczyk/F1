from typing import Any

from models.records.link import LinkRecord
from validation.records import RecordValidator


class CarRecord(LinkRecord, total=False):
    formula_category: str


def validate_car_record(record: dict[str, Any]) -> list[str]:
    errors = RecordValidator.require_link_dict(record, "car")
    errors.extend(RecordValidator.require_type(record, "formula_category", str))
    return errors
