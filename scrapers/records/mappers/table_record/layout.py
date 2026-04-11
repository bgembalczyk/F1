from typing import Any

from scrapers.records.mappers.table_record.base import TableRecordMapper


class LayoutTableRecordMapper:
    """Groups flat table rows into layout -> records structure.

    Normalization rules:
    - each row is first normalized with TableRecordMapper,
    - rows without non-empty layout string are ignored,
    - `layout` field is removed from grouped record entries.
    """

    def __init__(self, *, row_mapper: TableRecordMapper | None = None) -> None:
        self._row_mapper = row_mapper or TableRecordMapper()

    def map(
        self,
        payload: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        rows = payload
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            normalized_row = self._row_mapper.map(row)
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
