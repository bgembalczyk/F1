from collections.abc import Mapping
from typing import Any

from scrapers.parsers.contracts.constants_contracts import GroupParsingMixin
from scrapers.parsers.contracts.constants_contracts import RowMappingMixin
from scrapers.records.inputs.table_record import TableRecordInput


class TableRecordMapper(
    RowMappingMixin[TableRecordInput | Mapping[str, Any], dict[str, Any]],
    GroupParsingMixin[list[Mapping[str, Any]], dict[str, Any]],
):
    """Maps table rows to normalized dictionaries.

    Normalization rules:
    - row payload must be mapping,
    - key names are stringified and stripped,
    - nested mapping/list values are normalized recursively.
    """

    def map(self, payload: TableRecordInput | Mapping[str, Any]) -> dict[str, Any]:
        source = payload.payload if isinstance(payload, TableRecordInput) else payload
        if not isinstance(source, Mapping):
            msg = "Table mapper contract violation: payload must be mapping."
            raise TypeError(msg)
        return {
            str(key).strip(): self._normalize_value(value)
            for key, value in source.items()
        }

    def map_many(self, payloads: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return [self.map(payload) for payload in payloads]

    def map_row(
        self,
        row: TableRecordInput | Mapping[str, Any],
    ) -> dict[str, Any] | None:
        return self.map(row)

    def map_table(self, table: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return self.map_many(table)

    def parse_group(self, table: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return self.map_many(table)

    def _normalize_value(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            return {str(k).strip(): self._normalize_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._normalize_value(item) for item in value]
        return value
