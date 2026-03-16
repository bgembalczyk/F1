from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.grand_prix import GrandsPrixRecord


class GrandsPrixRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> GrandsPrixRecord:
        payload = dict(record)
        self.normalize_link_fields(payload, ["race_title"])
        self.normalize_string_field(payload, "race_status")
        self.normalize_seasons_fields(payload, ["years_held"])
        self.normalize_link_list_fields(payload, ["country"])
        self.normalize_int_fields(payload, ["circuits", "total"])
        self.set_defaults(payload, {"years_held": [], "country": []})
        return cast("GrandsPrixRecord", payload)
