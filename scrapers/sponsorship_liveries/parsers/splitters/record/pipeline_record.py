from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PipelineRecord:
    """Domain model for splitter pipeline records."""

    payload: dict[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.payload, dict):
            raise TypeError("PipelineRecord payload must be a dict[str, Any]")
        for key in self.payload:
            if not isinstance(key, str):
                raise TypeError("PipelineRecord keys must be str")

    @classmethod
    def from_input(cls, record: Mapping[str, Any] | PipelineRecord) -> PipelineRecord:
        if isinstance(record, PipelineRecord):
            return record
        if not isinstance(record, Mapping):
            raise TypeError("PipelineRecord input must be a mapping")
        return cls(dict(record))

    def get(self, key: str, default: Any = None) -> Any:
        return self.payload.get(key, default)

    def with_updates(self, **updates: Any) -> PipelineRecord:
        return PipelineRecord({**self.payload, **updates})

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)
