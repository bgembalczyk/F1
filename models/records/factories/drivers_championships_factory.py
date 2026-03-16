from collections.abc import Mapping
from typing import Any, cast

from models.records.base_factory import BaseRecordFactory
from models.records.driver_championships import DriversChampionshipsRecord


class DriversChampionshipsRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> DriversChampionshipsRecord:
        payload = dict(record)
        self.normalize_int_fields(payload, ["count"])
        payload["count"] = payload["count"] or 0
        self.normalize_seasons_fields(payload, ["seasons"])
        return cast("DriversChampionshipsRecord", payload)
