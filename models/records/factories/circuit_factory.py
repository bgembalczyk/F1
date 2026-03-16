from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.circuit import CircuitRecord
from models.records.factories.helpers import normalize_optional_link_or_string


class CircuitRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> CircuitRecord:
        payload = self.apply_spec(
            record,
            {
                "field_normalizers": {
                    "circuit_status": lambda value,
                    field: self.normalizer.normalize_status(
                        value,
                        ["current", "future", "former"],
                        field,
                    ),
                    "country": lambda value, field: normalize_optional_link_or_string(
                        self.normalizer,
                        value,
                        field,
                    ),
                },
                "list_field_normalizers": {
                    "link": ["circuit"],
                    "float": ["last_length_used_km", "last_length_used_mi"],
                    "int": ["turns", "grands_prix_held"],
                    "link_list": ["grands_prix"],
                    "seasons": ["seasons"],
                },
                "defaults": {"grands_prix": [], "seasons": []},
            },
        )
        return cast("CircuitRecord", payload)
