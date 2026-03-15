"""Serialization helpers for TableSchemaDSL.

Extracted from scrapers/base/table/table_schema.py to keep that module focused on the
core build logic.
"""

from typing import Any

from scrapers.base.table.columns.types.base import BaseColumn


def serialize_value(value: Any) -> Any:
    """Recursively convert a column-kwarg value to a JSON-safe type."""
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [serialize_value(item) for item in value]
    if isinstance(value, type):
        return f"{value.__module__}.{value.__name__}"
    if callable(value):
        return getattr(value, "__qualname__", repr(value))
    return repr(value)


def column_ref_payload(spec: Any) -> dict[str, Any]:
    """Return a serialisable ``{"class_path": ..., "kwargs": ...}`` payload."""
    if isinstance(spec.column, BaseColumn):
        class_path = (
            f"{spec.column.__class__.__module__}.{spec.column.__class__.__name__}"
        )
        kwargs = {
            key: serialize_value(value)
            for key, value in dict(getattr(spec.column, "__dict__", {})).items()
        }
        return {"class_path": class_path, "kwargs": kwargs}
    return {
        "class_path": spec.column.class_path,
        "kwargs": {k: serialize_value(v) for k, v in dict(spec.column.kwargs).items()},
    }
