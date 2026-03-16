from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.driver_championships import DriversChampionshipsRecord


class DriversChampionshipsRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> DriversChampionshipsRecord:
        payload = self.apply_spec(
            record,
            {
                "list_field_normalizers": {
                    "int": ["count"],
                    "seasons": ["seasons"],
                },
            },
        )
        payload["count"] = payload.get("count") or 0
        return cast("DriversChampionshipsRecord", payload)
