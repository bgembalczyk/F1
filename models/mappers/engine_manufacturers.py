from __future__ import annotations

from typing import Any, Mapping

from models.engine_manufacturer import EngineManufacturer


def from_scraped_engine_manufacturer(
    data: Mapping[str, Any] | EngineManufacturer,
) -> EngineManufacturer:
    if isinstance(data, EngineManufacturer):
        return data
    return EngineManufacturer(**dict(data))
