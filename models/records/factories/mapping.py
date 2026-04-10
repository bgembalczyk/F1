from dataclasses import dataclass
from typing import Any
from typing import Mapping
from warnings import warn


@dataclass(frozen=True, slots=True)
class MappingRecordFactory:
    """Backward-compatible mapping factory that returns plain dictionaries."""

    def build(self, record: Mapping[str, Any]) -> dict[str, Any]:
        return {**record}

    def create(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        warn(
            "MappingRecordFactory.create(payload) is deprecated; use build(record).",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.build(payload)
