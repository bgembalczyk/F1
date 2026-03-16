from collections.abc import Mapping
from typing import Any, cast

from models.records.base_factory import BaseRecordFactory
from models.records.constants import WIKI_SEASON_URL
from models.records.season import SeasonRecord


class SeasonRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> SeasonRecord:
        payload = dict(record)
        self.normalize_int_fields(payload, ["year"])
        self.normalize_string_field(payload, "url")
        if payload.get("year") is not None and not payload.get("url"):
            payload["url"] = WIKI_SEASON_URL.format(year=payload["year"])
        return cast("SeasonRecord", payload)
