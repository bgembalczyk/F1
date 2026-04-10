from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.circuit.circuit import CircuitRecord
from models.records.factories.base import BaseRecordFactory
from models.records.factories.registry.helpers import register_factory


@register_factory("circuit")
class CircuitRecordFactory(BaseRecordFactory):
    record_type = "circuit"

    def build(self, record: Mapping[str, Any]) -> CircuitRecord:
        payload = self.apply_spec(
            record,
            {
                "field_normalizers": {
                    "circuit_status": lambda value, _field: value,
                    "country": lambda value, _field: value,
                    "location": lambda value, _field: value,
                },
                "list_field_normalizers": {
                    "link": ["circuit"],
                    "float": ["last_length_used_km", "last_length_used_mi"],
                    "int": ["turns", "grands_prix_held"],
                    "link_list": ["grands_prix"],
                    "seasons": ["seasons"],
                },
                "defaults": {
                    "grands_prix": [],
                    "seasons": [],
                    "last_length_used_km": None,
                    "last_length_used_mi": None,
                    "turns": None,
                    "grands_prix_held": None,
                },
            },
        )
        self.normalize_status_field(
            payload,
            "circuit_status",
            ["current", "future", "former"],
        )
        self.normalize_link_like_field(payload, "country")
        self.normalize_location_field(payload, "location")
        return cast("CircuitRecord", payload)


__all__ = [
    "CircuitRecordFactory",
]
