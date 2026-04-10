from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from models.records.shared_axes import SHARED_SCHEMA_FRAGMENTS


SchemaFragment = Mapping[str, Any]


def compose_schema_fragments(*axes: str) -> dict[str, Any]:
    composed: dict[str, Any] = {
        "types": {},
        "nested": {},
        "allow_none": (),
    }
    for axis in axes:
        fragment = SHARED_SCHEMA_FRAGMENTS[axis]
        composed["types"].update(fragment.get("types", {}))
        composed["nested"].update(fragment.get("nested", {}))
        composed["allow_none"] = (*composed["allow_none"], *fragment.get("allow_none", ()))
    return composed


__all__ = ["SchemaFragment", "compose_schema_fragments", "SHARED_SCHEMA_FRAGMENTS"]
