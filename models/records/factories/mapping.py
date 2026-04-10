from collections.abc import Mapping
from typing import Any

from models.records.factories.compat import create_compat


class MappingRecordFactory:
    """Backward-compatible mapping factory that returns plain dictionaries."""

    def build(self, record: Mapping[str, Any]) -> dict[str, Any]:
        return {**record}

    def create(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return create_compat(payload, self.build)
