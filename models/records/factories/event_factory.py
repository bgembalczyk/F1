from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.event import EventRecord
from models.records.factories.helpers import (
    normalize_optional_link_list_or_link_or_string,
)


class EventRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> EventRecord:
        payload = dict(record)
        payload["event"] = normalize_optional_link_list_or_link_or_string(
            self.normalizer,
            payload.get("event"),
            "event",
        )
        payload["championship"] = self.normalizer.normalize_bool(
            payload.get("championship"),
        )
        return cast("EventRecord", payload)
