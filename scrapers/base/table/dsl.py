import importlib
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Iterable
from typing import Mapping

from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.schema import TableSchema


@dataclass(frozen=True)
class ColumnRef:
    class_path: str
    kwargs: Mapping[str, Any] = field(default_factory=dict)

    def build(self) -> BaseColumn:
        module_path, class_name = self.class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        column_cls = getattr(module, class_name)
        if isinstance(column_cls, type) and issubclass(column_cls, BaseColumn):
            return column_cls(**dict(self.kwargs))
        if callable(column_cls):
            instance = column_cls(**dict(self.kwargs))
            if isinstance(instance, BaseColumn):
                return instance
        raise TypeError(f"{self.class_path} is not a BaseColumn factory or subclass.")

    @classmethod
    def from_instance(cls, column: BaseColumn) -> "ColumnRef":
        class_path = f"{column.__class__.__module__}.{column.__class__.__name__}"
        kwargs = dict(getattr(column, "__dict__", {}))
        return cls(class_path=class_path, kwargs=kwargs)


@dataclass(frozen=True)
class ColumnSpec:
    header: str
    key: str
    column: BaseColumn | ColumnRef

    def build_column(self) -> BaseColumn:
        if isinstance(self.column, BaseColumn):
            return self.column
        return self.column.build()


def column(
        header: str,
        key: str,
        column_instance: BaseColumn | ColumnRef,
) -> ColumnSpec:
    return ColumnSpec(header=header, key=key, column=column_instance)


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
                raise ValueError("TableSchemaDSL column header must be non-empty.")
            if not spec.key.strip():
                raise ValueError("TableSchemaDSL column key must be non-empty.")
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
                    "column": self._column_ref_payload(spec),
                }
                for spec in self.columns
            ]
        }

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, dict):
            return {
                key: TableSchemaDSL._serialize_value(val) for key, val in value.items()
            }
        if isinstance(value, (list, tuple)):
            return [TableSchemaDSL._serialize_value(item) for item in value]
        if isinstance(value, type):
            return f"{value.__module__}.{value.__name__}"
        if callable(value):
            return getattr(value, "__qualname__", repr(value))
        return repr(value)

    @staticmethod
    def _column_ref_payload(spec: ColumnSpec) -> dict[str, Any]:
        if isinstance(spec.column, BaseColumn):
            ref = ColumnRef.from_instance(spec.column)
            kwargs = {
                key: TableSchemaDSL._serialize_value(value)
                for key, value in dict(ref.kwargs).items()
            }
            return {"class_path": ref.class_path, "kwargs": kwargs}
        return {
            "class_path": spec.column.class_path,
            "kwargs": {
                key: TableSchemaDSL._serialize_value(value)
                for key, value in dict(spec.column.kwargs).items()
            },
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
