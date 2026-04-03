from collections.abc import Mapping
from typing import Any
from typing import cast

from models.mappers.field_aliases import FIELD_ALIASES
from models.records.base_factory import BaseRecordFactory
from models.records.factories.registry import register_factory
from models.records.grand_prix import GrandsPrixRecord


@register_factory("grands_prix")
class GrandsPrixRecordFactory(BaseRecordFactory):
    record_type = "grands_prix"

    def build(self, record: Mapping[str, Any]) -> GrandsPrixRecord:
        payload = self.apply_spec(
            record,
            {
                "aliases": FIELD_ALIASES["grands_prix"],
                "record_name": "grands_prix",
                "field_normalizers": {
                    "race_status": lambda value,
                    _field: self.normalizer.normalize_string(
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
