from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class RecordBuilder(Protocol):
    """Canonical public contract for record factories/builders."""

    def build(self, record: Mapping[str, Any]) -> Any: ...


@runtime_checkable
class RecordFactory(Protocol):
    """Deprecated legacy adapter kept for backwards compatibility only."""

    def create(self, payload: Mapping[str, Any]) -> Any: ...


RecordBuilderProtocol = RecordBuilder
RecordFactoryProtocol = RecordFactory

__all__ = [
    "RecordBuilder",
    "RecordBuilderProtocol",
]
