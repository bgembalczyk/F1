from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

from models.records.factories.build import RECORD_BUILDERS
from models.records.factories.build import RecordType

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping


class RecordFactory(Protocol):
    """Unified contract for record creation used by scraper configuration."""

    def create(self, payload: Mapping[str, Any]) -> Any: ...


@dataclass(frozen=True, slots=True)
class MappingRecordFactory:
    """Backward-compatible mapping factory that returns plain dictionaries."""

    def create(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return {**payload}


@dataclass(frozen=True, slots=True)
class CallableRecordFactoryAdapter:
    """Adapter for callable- and class-based legacy record factories."""

    factory: Callable[[dict[str, Any]], Any] | type

    def create(self, payload: Mapping[str, Any]) -> Any:
        if isinstance(self.factory, type):
            return self.factory(**dict(payload))
        return self.factory(dict(payload))


@dataclass(frozen=True, slots=True)
class RecordFactoryAdapters:
    """Factory helpers for the unified RecordFactory contract."""

    adapter_builder: Callable[
        [Callable[[dict[str, Any]], Any] | type],
        RecordFactory,
    ] = CallableRecordFactoryAdapter

    def callable(
        self,
        factory: Callable[[dict[str, Any]], Any] | type,
    ) -> RecordFactory:
        if not callable(factory):
            msg = "Record factory must be callable or a record type."
            raise TypeError(msg)
        return self.adapter_builder(factory)

    def builders(self, record_type: RecordType | str) -> RecordFactory:
        if isinstance(record_type, str) and not record_type.strip():
            msg = "record_type cannot be empty."
            raise ValueError(msg)
        return self.adapter_builder(
            factory=lambda payload: RECORD_BUILDERS.build(record_type, payload),
        )


RECORD_FACTORIES = RecordFactoryAdapters()
