from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.circuit_complete import CircuitCompleteRecord


class CircuitCompleteRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> CircuitCompleteRecord:
        payload = self.apply_spec(
            record,
            {
                "list_field_normalizers": {
                    "link_list": ["grands_prix"],
                    "seasons": ["seasons"],
                    "int": ["grands_prix_held"],
                },
                "defaults": {
                    "history": [],
                    "layouts": [],
                    "grands_prix": [],
                    "seasons": [],
                },
            },
        )
        return cast("CircuitCompleteRecord", payload)
