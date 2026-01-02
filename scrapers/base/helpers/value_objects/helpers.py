from typing import Any
from typing import Mapping

from scrapers.base.helpers.value_objects.lap_record import LapRecord


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


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


def normalize_iso(value: Any) -> str | None:
    if isinstance(value, list):
        value = value[0] if value else None
    return normalize_text(value)


def as_lap_record(record: LapRecord | Mapping[str, Any]) -> LapRecord:
    if isinstance(record, LapRecord):
        return record
    return LapRecord.from_dict(record)
