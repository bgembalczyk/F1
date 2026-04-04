from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.driver_championships import DriversChampionshipsRecord
from models.records.factories.registry import register_factory
from models.value_objects.drivers_championships import DriversChampionships


@register_factory("drivers_championships")
class DriversChampionshipsRecordFactory(BaseRecordFactory):
    record_type = "drivers_championships"

    def build(
        self,
        record: Mapping[str, Any] | DriversChampionships | int | str | None,
    ) -> DriversChampionshipsRecord:
        if isinstance(record, DriversChampionships):
            payload = record.to_dict()
        elif isinstance(record, Mapping):
            payload = self.apply_spec(
                record,
                {
                    "list_field_normalizers": {
                        "int": ["count"],
                        "seasons": ["seasons"],
                    },
                },
            )
        else:
            payload = {"count": record, "seasons": []}
            payload = self.apply_spec(
                payload,
                {
                    "list_field_normalizers": {
                        "int": ["count"],
                        "seasons": ["seasons"],
                    },
                },
            )
        payload["count"] = payload.get("count") or 0
        return cast("DriversChampionshipsRecord", payload)
