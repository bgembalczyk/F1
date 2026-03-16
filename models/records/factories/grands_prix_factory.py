from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.grand_prix import GrandsPrixRecord


class GrandsPrixRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> GrandsPrixRecord:
        payload = self.apply_spec(
            record,
            {
                "field_normalizers": {
                    "race_status": lambda value, _field: self.normalizer.normalize_string(
                        value,
                    ),
                },
                "list_field_normalizers": {
                    "link": ["race_title"],
                    "seasons": ["years_held"],
                    "link_list": ["country"],
                    "int": ["circuits", "total"],
                },
                "defaults": {"years_held": [], "country": []},
            },
        )
        return cast("GrandsPrixRecord", payload)
