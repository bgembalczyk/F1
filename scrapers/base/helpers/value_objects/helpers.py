from collections.abc import Mapping
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from scrapers.base.helpers.value_objects.lap_record import LapRecord


def normalize_seconds(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return float(stripped)
        except ValueError:
            return None
    return None


def as_lap_record(record: "LapRecord" | Mapping[str, Any]):
    from scrapers.base.helpers.value_objects.lap_record import LapRecord

    if isinstance(record, LapRecord):
        return record
    return LapRecord.from_dict(record)
