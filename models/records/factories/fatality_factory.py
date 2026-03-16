from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.factories.car_factory import CarRecordFactory
from models.records.factories.event_factory import EventRecordFactory
from models.records.factories.registry import register_factory
from models.records.fatality import FatalityRecord


@register_factory("fatality")
class FatalityRecordFactory(BaseRecordFactory):
    record_type = "fatality"

    def __init__(self, normalizer=None):
        super().__init__(normalizer)
        self.event_factory = EventRecordFactory(self.normalizer)
        self.car_factory = CarRecordFactory(self.normalizer)

    def build(self, record: Mapping[str, Any]) -> FatalityRecord:
        payload = self.apply_spec(
            record,
            {
                "field_normalizers": {
                    "session": lambda value, _field: self.normalizer.normalize_string(
                        value,
                    ),
                },
                "list_field_normalizers": {
                    "link": ["driver", "circuit"],
                    "int": ["age"],
                },
                "nested_factories": {
                    "event": self.event_factory,
                    "car": self.car_factory,
                },
            },
        )

        car = payload.get("car")
        if not isinstance(car, Mapping) and car:
            payload["car"] = self.normalizer.normalize_link(car, "car")

        return cast("FatalityRecord", payload)
