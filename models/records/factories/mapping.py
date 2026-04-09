from dataclasses import dataclass
from typing import Any
from typing import Mapping


@dataclass(frozen=True, slots=True)
class MappingRecordFactory:
    """Backward-compatible mapping factory that returns plain dictionaries."""

    def create(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return {**payload}


