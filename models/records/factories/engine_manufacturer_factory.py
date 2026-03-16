from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.engine_manufacturer import EngineManufacturerRecord


class EngineManufacturerRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> EngineManufacturerRecord:
        payload = dict(record)
        self.normalize_link_fields(payload, ["manufacturer"])
        payload["manufacturer_status"] = self.normalizer.normalize_status(
            payload.get("manufacturer_status"),
            ["current", "former"],
            "manufacturer_status",
        )
        self.normalize_link_list_fields(payload, ["engines_built_in"])
        self.normalize_seasons_fields(payload, ["seasons"])
        self.normalize_int_fields(
            payload,
            [
                "races_entered",
                "races_started",
                "wins",
                "poles",
                "fastest_laps",
                "podiums",
                "wcc",
                "wdc",
            ],
        )
        self.normalize_float_fields(payload, ["points"])
        self.set_defaults(payload, {"engines_built_in": [], "seasons": []})
        return cast("EngineManufacturerRecord", payload)
