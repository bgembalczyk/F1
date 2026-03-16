from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.circuit import CircuitRecord
from models.records.factories.helpers import normalize_optional_link_or_string


class CircuitRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> CircuitRecord:
        payload = dict(record)
        self.normalize_link_fields(payload, ["circuit"])
        payload["circuit_status"] = self.normalizer.normalize_status(
            payload.get("circuit_status"),
            ["current", "future", "former"],
            "circuit_status",
        )
        self.normalize_float_fields(
            payload,
            ["last_length_used_km", "last_length_used_mi"],
        )
        self.normalize_int_fields(payload, ["turns", "grands_prix_held"])
        self.normalize_link_list_fields(payload, ["grands_prix"])
        self.normalize_seasons_fields(payload, ["seasons"])
        payload["country"] = normalize_optional_link_or_string(
            self.normalizer,
            payload.get("country"),
            "country",
        )
        self.set_defaults(payload, {"grands_prix": [], "seasons": []})
        return cast("CircuitRecord", payload)
