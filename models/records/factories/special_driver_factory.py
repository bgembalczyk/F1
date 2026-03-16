from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.factories.helpers import normalize_points
from models.records.factories.registry import register_factory
from models.records.special_driver import SpecialDriverRecord


@register_factory("special_driver")
class SpecialDriverRecordFactory(BaseRecordFactory):
    record_type = "special_driver"

    def build(self, record: Mapping[str, Any]) -> SpecialDriverRecord:
        payload = self.apply_spec(
            record,
            {
                "field_normalizers": {
                    "points": lambda value, _field: normalize_points(
                        self.normalizer,
                        value,
                    ),
                },
                "list_field_normalizers": {
                    "link": ["driver"],
                    "seasons": ["seasons"],
                    "link_list": ["teams"],
                    "int": ["entries", "starts"],
                },
                "defaults": {"seasons": [], "teams": []},
            },
        )
        return cast("SpecialDriverRecord", payload)
