from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from functools import partial
from typing import Any
from typing import TYPE_CHECKING
from typing import Callable
from typing import overload

from models.records.factories.registry import FACTORY_REGISTRY
from models.records.factories.registry import get_factory

if TYPE_CHECKING:
    from models.records.base_factory import BaseRecordFactory


class RecordType(str, Enum):
    LINK = "link"
    SEASON = "season"
    DRIVERS_CHAMPIONSHIPS = "drivers_championships"
    DRIVER = "driver"
    SPECIAL_DRIVER = "special_driver"
    CONSTRUCTOR = "constructor"
    CIRCUIT = "circuit"
    EVENT = "event"
    CAR = "car"
    FATALITY = "fatality"
    SEASON_SUMMARY = "season_summary"
    GRANDS_PRIX = "grands_prix"
    CIRCUIT_DETAILS = "circuit_details"
    CIRCUIT_COMPLETE = "circuit_complete"
    ENGINE_MANUFACTURER = "engine_manufacturer"


class RecordBuilders:
    """Object facade for building normalized record models."""

    def __init__(
        self,
        factory_registry: Mapping[str, BaseRecordFactory] | None = None,
    ):
        self._factory_registry = factory_registry or FACTORY_REGISTRY

    def _factory_for(self, record_type: RecordType | str) -> BaseRecordFactory:
        resolved_type = (
            record_type.value if isinstance(record_type, RecordType) else record_type
        )
        return get_factory(resolved_type, self._factory_registry)

    @overload
    def build(self, record_type: RecordType, record: Mapping[str, Any]) -> Any: ...

    @overload
    def build(self, record_type: str, record: Mapping[str, Any]) -> Any: ...

    def build(self, record_type: RecordType | str, record: Mapping[str, Any]) -> Any:
        return self._factory_for(record_type).build(record)

    def __getattr__(self, name: str) -> Callable[[Mapping[str, Any]], Any]:
        if name in RecordType._value2member_map_:
            return partial(self.build, RecordType(name))

        message = f"{self.__class__.__name__!s} has no attribute {name!r}"
        raise AttributeError(message)


RECORD_BUILDERS = RecordBuilders()


@overload
def build_record(record_type: RecordType, record: Mapping[str, Any]) -> Any: ...


@overload
def build_record(record_type: str, record: Mapping[str, Any]) -> Any: ...


def build_record(record_type: RecordType | str, record: Mapping[str, Any]) -> Any:
    return RECORD_BUILDERS.build(record_type, record)


def _build_convenience(record_type: RecordType) -> Callable[[Mapping[str, Any]], Any]:
    return partial(build_record, record_type)


for _record_type in RecordType:
    globals()[f"build_{_record_type.value}_record"] = _build_convenience(_record_type)


__all__ = [
    "RECORD_BUILDERS",
    "RecordBuilders",
    "RecordType",
    "build_record",
    *[f"build_{record_type.value}_record" for record_type in RecordType],
]
