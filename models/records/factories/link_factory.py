from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.factories.registry import register_factory
from models.records.link import LinkRecord


@register_factory("link")
class LinkRecordFactory(BaseRecordFactory):
    record_type = "link"

    def build(self, record: Mapping[str, Any]) -> LinkRecord:
        normalized = self.normalizer.normalize_link(record, "link") or {
            "text": "",
            "url": None,
        }
        return cast("LinkRecord", normalized)
