from collections.abc import Iterable
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.dsl.column import ColumnRef
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.serialization import column_ref_payload
from scrapers.base.table.schema import TableSchema


@dataclass(frozen=True)
class TableSchemaDSL:
    columns: Iterable[ColumnSpec]

    def build(self) -> TableSchema:
        column_map: dict[str, str] = {}
        columns: dict[str, BaseColumn] = {}
        key_signatures: dict[str, tuple[str, dict[str, Any]]] = {}
        key_instances: dict[str, BaseColumn] = {}
        duplicate_keys: set[str] = set()

        for spec in self.columns:
            if not spec.header.strip():
                msg = "TableSchemaDSL column header must be non-empty."
                raise ValueError(msg)
            if not spec.key.strip():
                msg = "TableSchemaDSL column key must be non-empty."
                raise ValueError(msg)
            column_map[spec.header] = spec.key
            column_instance = spec.build_column()
            signature = ColumnRef.from_instance(column_instance)
            if spec.key in key_signatures and key_signatures[spec.key] != (
                signature.class_path,
                dict(signature.kwargs),
            ):
                duplicate_keys.add(spec.key)
            else:
                key_signatures[spec.key] = (
                    signature.class_path,
                    dict(signature.kwargs),
                )
            key_instances.setdefault(spec.key, column_instance)
            columns[spec.header] = column_instance

        for key in key_signatures:
            if key in duplicate_keys:
                continue
            columns[key] = key_instances[key]

        return TableSchema(column_map=column_map, columns=columns)

    def to_dict(self) -> dict[str, Any]:
        return {
            "columns": [
                {
                    "header": spec.header,
                    "key": spec.key,
                    "column": column_ref_payload(spec),
                }
                for spec in self.columns
            ],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "TableSchemaDSL":
        columns_data = data.get("columns", [])
        specs: list[ColumnSpec] = []
        for item in columns_data:
            column_data = item.get("column", {})
            column_ref = ColumnRef(
                class_path=column_data["class_path"],
                kwargs=column_data.get("kwargs", {}),
            )
            specs.append(
                ColumnSpec(
                    header=item["header"],
                    key=item["key"],
                    column=column_ref,
                ),
            )
        return cls(columns=specs)

    @classmethod
    def from_config(cls, config: Any) -> "TableSchemaDSL":
        column_specs: list[ColumnSpec] = []
        for header, key in config.column_map.items():
            column_instance = config.columns.get(key, config.default_column)
            column_specs.append(
                ColumnSpec(
                    header=header,
                    key=key,
                    column=ColumnRef.from_instance(column_instance),
                ),
            )
        return cls(columns=column_specs)
