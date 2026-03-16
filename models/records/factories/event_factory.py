from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.event import EventRecord
from models.records.factories.helpers import (
    normalize_optional_link_list_or_link_or_string,
)
from models.records.factories.registry import register_factory


@register_factory("event")
class EventRecordFactory(BaseRecordFactory):
    record_type = "event"

    def build(self, record: Mapping[str, Any]) -> EventRecord:
        payload = self.apply_spec(
            record,
            {
                "field_normalizers": {
                    "event": lambda value,
                    field: normalize_optional_link_list_or_link_or_string(
                        self.normalizer,
                        value,
                        field,
                    ),
                    "championship": lambda value,
                    _field: self.normalizer.normalize_bool(
                        value,
                    ),
                },
            },
        )
        return cast("EventRecord", payload)
