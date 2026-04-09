from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.factories.base import BaseRecordFactory
from models.records.factories.car import CarRecordFactory
from models.records.factories.event import EventRecordFactory
from models.records.factories.registry.helpers import register_factory
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


__all__ = ["FatalityRecordFactory"]
