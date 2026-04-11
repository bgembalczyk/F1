from collections.abc import Mapping
from typing import Any


class MappingRecordFactory:
    """Backward-compatible mapping factory that returns plain dictionaries."""

    def build(self, record: Mapping[str, Any]) -> dict[str, Any]:
        return {**record}
