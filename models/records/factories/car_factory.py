from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.car import CarRecord


class CarRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> CarRecord:
        payload = dict(record)
        link = self.normalizer.normalize_link(payload, "car") or {
            "text": "",
            "url": None,
        }
        payload["text"] = link["text"]
        payload["url"] = link["url"]
        formula_category = self.normalizer.normalize_string(
            payload.get("formula_category"),
        )
        if formula_category:
            payload["formula_category"] = formula_category
        else:
            payload.pop("formula_category", None)
        return cast("CarRecord", payload)
