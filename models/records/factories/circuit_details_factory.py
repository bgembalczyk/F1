from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.circuit_details import CircuitDetailsRecord
from models.records.factories.registry import register_factory


@register_factory("circuit_details")
class CircuitDetailsRecordFactory(BaseRecordFactory):
    record_type = "circuit_details"

    def build(self, record: Mapping[str, Any]) -> CircuitDetailsRecord:
        payload = self.apply_spec(record, {"defaults": {"infobox": {}, "tables": []}})
        return cast("CircuitDetailsRecord", payload)
