from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from typing import Protocol

from models.records.factories.build import RECORD_BUILDERS


class RecordFactory(Protocol):
    """Unified contract for record creation used by scraper configuration."""

    def create(self, payload: Mapping[str, Any]) -> Any: ...


@dataclass(frozen=True, slots=True)
class MappingRecordFactory:
    """Adapter returning plain dict from mapping payload."""

    def create(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return dict(payload)


@dataclass(frozen=True, slots=True)
class CallableRecordFactoryAdapter:
    """Adapter for callable- and class-based legacy record factories."""

    factory: Callable[[dict[str, Any]], Any] | type

    def create(self, payload: Mapping[str, Any]) -> Any:
        if isinstance(self.factory, type):
            return self.factory(**dict(payload))
        return self.factory(dict(payload))


@dataclass(frozen=True, slots=True)
class RecordBuildersAdapter:
    """Adapter over models.records.factories.build.RECORD_BUILDERS."""

    record_type: str

    def create(self, payload: Mapping[str, Any]) -> Any:
        return RECORD_BUILDERS.build(self.record_type, payload)


class RecordFactoryAdapters:
    """Factory helpers for the unified RecordFactory contract."""

    @staticmethod
    def mapping() -> RecordFactory:
        return MappingRecordFactory()

    @staticmethod
    def callable(factory: Callable[[dict[str, Any]], Any] | type) -> RecordFactory:
        return CallableRecordFactoryAdapter(factory=factory)

    @staticmethod
    def builders(record_type: str) -> RecordFactory:
        return RecordBuildersAdapter(record_type=record_type)


RECORD_FACTORIES = RecordFactoryAdapters()
