from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.circuit_complete import CircuitCompleteRecord


class CircuitCompleteRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> CircuitCompleteRecord:
        payload = dict(record)
        self.normalize_link_list_fields(payload, ["grands_prix"])
        self.normalize_seasons_fields(payload, ["seasons"])
        self.normalize_int_fields(payload, ["grands_prix_held"])
        self.set_defaults(
            payload,
            {
                "history": [],
                "layouts": [],
                "grands_prix": [],
                "seasons": [],
            },
        )
        return cast("CircuitCompleteRecord", payload)
