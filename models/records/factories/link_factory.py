from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.link import LinkRecord


class LinkRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> LinkRecord:
        normalized = self.normalizer.normalize_link(record, "link") or {
            "text": "",
            "url": None,
        }
        return cast("LinkRecord", normalized)
