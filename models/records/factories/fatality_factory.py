from collections.abc import Mapping
from typing import Any, cast

from models.records.base_factory import BaseRecordFactory
from models.records.fatality import FatalityRecord
from models.records.factories.car_factory import CarRecordFactory
from models.records.factories.event_factory import EventRecordFactory


class FatalityRecordFactory(BaseRecordFactory):
    def __init__(self, normalizer=None):
        super().__init__(normalizer)
        self.event_factory = EventRecordFactory(self.normalizer)
        self.car_factory = CarRecordFactory(self.normalizer)

    def build(self, record: Mapping[str, Any]) -> FatalityRecord:
        payload = dict(record)
        self.normalize_link_fields(payload, ["driver", "circuit"])
        self.normalize_int_fields(payload, ["age"])

        event = payload.get("event")
        payload["event"] = self.event_factory.build(event) if isinstance(event, Mapping) else None

        car = payload.get("car")
        payload["car"] = self.car_factory.build(car) if isinstance(car, Mapping) else self.normalizer.normalize_link(car, "car") if car else None

        self.normalize_string_field(payload, "session")
        return cast("FatalityRecord", payload)
