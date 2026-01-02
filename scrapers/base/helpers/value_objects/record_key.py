from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RecordKey:
    driver_text: str
    vehicle_text: str
    year: str
    time_seconds: float | None = None

    def to_tuple(self) -> tuple[str, str, str, float | None]:
        return self.driver_text, self.vehicle_text, self.year, self.time_seconds

    def to_dict(self) -> dict[str, Any]:
        return {
            "driver_text": self.driver_text,
            "vehicle_text": self.vehicle_text,
            "year": self.year,
            "time_seconds": self.time_seconds,
        }
