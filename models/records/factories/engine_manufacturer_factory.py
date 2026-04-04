from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.engine_manufacturer import EngineManufacturerRecord
from models.records.factories.registry import register_factory


@register_factory("engine_manufacturer")
class EngineManufacturerRecordFactory(BaseRecordFactory):
    record_type = "engine_manufacturer"

    def build(self, record: Mapping[str, Any]) -> EngineManufacturerRecord:
        payload = self.apply_spec(
            record,
            {
                "field_normalizers": {
                    "manufacturer_status": lambda value, field: (
                        self.normalizer.normalize_status(
                            value,
                            ["current", "former"],
                            field,
                        )
                    ),
                },
                "list_field_normalizers": {
                    "link": ["manufacturer"],
                    "link_list": ["engines_built_in"],
                    "seasons": ["seasons"],
                    "int": [
                        "races_entered",
                        "races_started",
                        "wins",
                        "poles",
                        "fastest_laps",
                        "podiums",
                        "wcc",
                        "wdc",
                    ],
                    "float": ["points"],
                },
                "defaults": {"engines_built_in": [], "seasons": []},
            },
        )
        return cast("EngineManufacturerRecord", payload)
