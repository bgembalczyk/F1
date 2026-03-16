from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.circuit_details import CircuitDetailsRecord


class CircuitDetailsRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> CircuitDetailsRecord:
        payload = dict(record)
        self.set_defaults(payload, {"infobox": {}, "tables": []})
        return cast("CircuitDetailsRecord", payload)
