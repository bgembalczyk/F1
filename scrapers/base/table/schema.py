from collections.abc import Mapping
from dataclasses import dataclass

from scrapers.base.table.columns.types.base import BaseColumn


@dataclass(frozen=True)
class TableSchema:
    column_map: Mapping[str, str]
    columns: Mapping[str, BaseColumn]


class TableSchemaBuilder:
    def __init__(self) -> None:
        self._column_map: dict[str, str] = {}
        self._columns: dict[str, BaseColumn] = {}

    def map(self, header: str, key: str, column: BaseColumn) -> "TableSchemaBuilder":
        if not isinstance(header, str) or not header.strip():
            msg = "TableSchemaBuilder.map header must be a non-empty string."
            raise ValueError(
                msg,
            )
        if not isinstance(key, str) or not key.strip():
            msg = "TableSchemaBuilder.map key must be a non-empty string."
            raise ValueError(msg)
        if not isinstance(column, BaseColumn):
            msg = "TableSchemaBuilder.map column must be a BaseColumn instance."
            raise ValueError(
                msg,
            )
        self._column_map[header] = key
        self._columns[key] = column
        return self

    def build(self) -> TableSchema:
        return TableSchema(
            column_map=dict(self._column_map),
            columns=dict(self._columns),
        )
