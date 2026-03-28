from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scrapers.base.helpers.normalize import normalize_auto_value


@dataclass(frozen=True)
class GrandPrixByYearRecordInput:
    """Input contract for by-year grand prix mapper.

    Input:
    - record: dict parsed from table row
    Output:
    - normalized record dict or None for "not held" rows.
    """

    record: dict[str, Any]


class GrandPrixByYearRecordMapper:
    """Normalizes by-year records and filters synthetic "not held" rows.

    Normalization rules:
    - preserves source keys and values via shallow copy,
    - row is dropped when canonical Not held pattern is detected
      across driver/chassis/engine/location.circuit fields,
    - supports wiki-mark normalization when evaluating text equality.
    """

    def map(
        self,
        payload: GrandPrixByYearRecordInput | dict[str, Any],
    ) -> dict[str, Any] | None:
        record = (
            payload.record
            if isinstance(payload, GrandPrixByYearRecordInput)
            else payload
        )
        if self._is_not_held_record(record):
            return None
        return dict(record)

    def _is_not_held_record(self, record: dict[str, Any]) -> bool:
        report_text = self._get_text(record.get("report"))
        location = record.get("location")
        layout_text = location.get("layout") if isinstance(location, dict) else None
        circuit_text = (
            self._get_text(location.get("circuit"))
            if isinstance(location, dict)
            else None
        )
        driver_text = self._list_text(record.get("driver"))
        chassis_text = self._get_text(record.get("chassis_constructor"))
        engine_text = self._get_text(record.get("engine_constructor"))
        if not all([driver_text, chassis_text, engine_text, circuit_text]):
            return False
        if not (driver_text == chassis_text == engine_text == circuit_text):
            return False
        if driver_text == "Not held":
            return True
        return bool(report_text and report_text.lower().startswith("not held")) or bool(
            layout_text
            and layout_text.lower().startswith(("not held due to", "cancelled due to")),
        )

    @staticmethod
    def _get_text(value: Any) -> str | None:
        normalized = normalize_auto_value(value, strip_marks=True, drop_empty=True)
        if isinstance(normalized, dict):
            text = normalized.get("text")
            return text if isinstance(text, str) and text else None
        if isinstance(normalized, str):
            return normalized or None
        return None

    def _list_text(self, items: Any) -> str | None:
        normalized = normalize_auto_value(items, strip_marks=True, drop_empty=True)
        if not isinstance(normalized, list) or not normalized:
            return None
        first_text = self._get_text(normalized[0])
        if not first_text:
            return None
        return (
            first_text
            if all(self._get_text(item) == first_text for item in normalized)
            else None
        )


__all__ = ["GrandPrixByYearRecordInput", "GrandPrixByYearRecordMapper"]
