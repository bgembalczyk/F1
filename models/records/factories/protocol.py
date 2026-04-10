from __future__ import annotations

from typing import Any
from typing import Mapping
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class RecordBuilder(Protocol):
    """Primary contract for record factories/builders."""

    def build(self, record: Mapping[str, Any]) -> Any: ...


@runtime_checkable
class RecordFactory(Protocol):
    """Deprecated adapter contract kept for legacy code paths."""

    def create(self, payload: Mapping[str, Any]) -> Any: ...


# Backward-compatible aliases.
RecordFactoryProtocol = RecordBuilder
RecordBuilderProtocol = RecordBuilder

__all__ = [
    "RecordBuilder",
    "RecordFactory",
    "RecordFactoryProtocol",
    "RecordBuilderProtocol",
]
