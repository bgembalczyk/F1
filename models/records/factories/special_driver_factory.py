from collections.abc import Mapping
from typing import Any, cast

from models.records.base_factory import BaseRecordFactory
from models.records.factories.helpers import normalize_points
from models.records.special_driver import SpecialDriverRecord


class SpecialDriverRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> SpecialDriverRecord:
        payload = dict(record)
        self.normalize_link_fields(payload, ["driver"])
        self.normalize_seasons_fields(payload, ["seasons"])
        self.normalize_link_list_fields(payload, ["teams"])
        self.normalize_int_fields(payload, ["entries", "starts"])
        payload["points"] = normalize_points(self.normalizer, payload.get("points"))
        self.set_defaults(payload, {"seasons": [], "teams": []})
        return cast("SpecialDriverRecord", payload)
