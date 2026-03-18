from collections.abc import Mapping
from typing import Any
from typing import cast

from models.domain_utils.season_urls import build_season_url
from models.records.base_factory import BaseRecordFactory
from models.records.factories.registry import register_factory
from models.records.season import SeasonRecord


@register_factory("season")
class SeasonRecordFactory(BaseRecordFactory):
    record_type = "season"

    def build(self, record: Mapping[str, Any]) -> SeasonRecord:
        payload = self.apply_spec(
            record,
            {
                "field_normalizers": {
                    "url": lambda value, _field: self.normalizer.normalize_string(
                        value,
                    ),
                },
                "list_field_normalizers": {"int": ["year"]},
            },
        )
        if payload.get("year") is not None and not payload.get("url"):
            payload["url"] = build_season_url(payload["year"])
        return cast("SeasonRecord", payload)
