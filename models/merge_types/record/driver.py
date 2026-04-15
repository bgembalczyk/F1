from __future__ import annotations

from dataclasses import dataclass

from models.domain_model import DomainModel

from models.merge_types.constants import RecordDict
from models.merge_types.driver_series_stats import DriverSeriesStats
from models.merge_types.link_value import LinkValue


@dataclass(slots=True)
class DriverRecordModel(DomainModel):
    raw: RecordDict

    @classmethod
    def from_object(cls, value: object) -> DriverRecordModel | None:
        if not isinstance(value, dict):
            return None
        record: RecordDict = value
        return cls(raw=record)

    def dedupe_key(self) -> str | None:
        driver_url = self.raw.get("driver_url")
        if isinstance(driver_url, str) and driver_url:
            return driver_url

        driver = LinkValue.from_object(self.raw.get("driver"))
        if driver is None:
            return None
        return driver.url

    def extract_identity(self) -> tuple[object | None, object | None]:
        return self.raw.get("driver"), self.raw.get("nationality")

    def extract_series_stats(self) -> DriverSeriesStats:
        payload = {
            key: value
            for key, value in self.raw.items()
            if key not in {"driver", "nationality"}
        }
        return DriverSeriesStats.from_dict(payload)

    def to_dict(self) -> RecordDict:
        return self.raw
