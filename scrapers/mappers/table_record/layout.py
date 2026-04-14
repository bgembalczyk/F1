from collections.abc import Mapping
from typing import Any


class LayoutTableRecordMapper:
    """Groups flat table rows into layout -> records structure.

    Normalization rules:
    - each row is first normalized (keys stringified and stripped),
    - rows without non-empty layout string are ignored,
    - `layout` field is removed from grouped record entries.
    """

    def map(
        self,
        payload: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        rows = payload
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            normalized_row = self._normalize_row(row)
            layout_name = normalized_row.get("layout")
            if not isinstance(layout_name, str) or not layout_name.strip():
                continue
            row_export = {
                key: value for key, value in normalized_row.items() if key != "layout"
            }
            grouped.setdefault(layout_name.strip(), []).append(row_export)
        return [
            {"layout": name, "lap_records": records}
            for name, records in grouped.items()
        ]

    @staticmethod
    def _normalize_row(row: Mapping[str, Any]) -> dict[str, Any]:
        return {
            str(key).strip(): LayoutTableRecordMapper._normalize_value(value)
            for key, value in row.items()
        }

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        if isinstance(value, Mapping):
            return {
                str(k).strip(): LayoutTableRecordMapper._normalize_value(v)
                for k, v in value.items()
            }
        if isinstance(value, list):
            return [LayoutTableRecordMapper._normalize_value(item) for item in value]
        return value
