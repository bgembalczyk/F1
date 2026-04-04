from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PipelineRecord:
    """Thin validated wrapper around the splitter record payload mapping."""

    payload: dict[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.payload, dict):
            msg = "PipelineRecord payload must be a dict[str, Any]"
            raise TypeError(msg)
        for key in self.payload:
            if not isinstance(key, str):
                msg = "PipelineRecord keys must be str"
                raise TypeError(msg)

    @classmethod
    def from_input(cls, record: Mapping[str, Any] | PipelineRecord) -> PipelineRecord:
        if isinstance(record, PipelineRecord):
            return record
        if not isinstance(record, Mapping):
            msg = "PipelineRecord input must be a mapping"
            raise TypeError(msg)
        return cls(dict(record))
