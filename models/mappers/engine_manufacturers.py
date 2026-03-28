from collections.abc import Mapping
from typing import Any

from models.validation.engine_manufacturer import EngineManufacturer


def from_scraped_engine_manufacturer(
    data: Mapping[str, Any] | EngineManufacturer,
) -> EngineManufacturer:
    if isinstance(data, EngineManufacturer):
        return data
    return EngineManufacturer(**dict(data))
