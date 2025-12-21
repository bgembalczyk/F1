from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class NormalizedTime:
    text: str | None = None
    seconds: float | None = None

    @classmethod
    def from_value(cls, value: Any) -> NormalizedTime | None:
        if value is None:
            return None
        if isinstance(value, NormalizedTime):
            return value
        if isinstance(value, Mapping):
            text = value.get("text")
            seconds = value.get("seconds")
            seconds_val = float(seconds) if isinstance(seconds, (int, float)) else None
            text_val = str(text).strip() if text is not None else None
            return cls(text=text_val or None, seconds=seconds_val)
        if isinstance(value, (int, float)):
            return cls(text=None, seconds=float(value))
        return cls(text=str(value).strip(), seconds=None)

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "seconds": self.seconds}


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


@dataclass
class LapRecord:
    data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        time_val = self.data.get("time")
        if isinstance(time_val, Mapping) or isinstance(time_val, NormalizedTime):
            normalized = NormalizedTime.from_value(time_val)
            if normalized is not None:
                self.data["time"] = normalized

        if "class" in self.data and "class_" not in self.data:
            self.data["class_"] = self.data.get("class")

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> LapRecord:
        return cls(data=dict(payload))

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in self.data.items():
            if isinstance(value, NormalizedTime):
                result[key] = value.to_dict()
            elif hasattr(value, "to_dict") and callable(value.to_dict):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def setdefault(self, key: str, default: Any = None) -> Any:
        return self.data.setdefault(key, default)

    def pop(self, key: str, default: Any = None) -> Any:
        return self.data.pop(key, default)

    def items(self) -> Iterable[tuple[str, Any]]:
        return self.data.items()

    def keys(self) -> Iterable[str]:
        return self.data.keys()

    def update(self, other: Mapping[str, Any]) -> None:
        self.data.update(other)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if key == "time" and not isinstance(value, NormalizedTime):
            normalized = NormalizedTime.from_value(value)
            if normalized is not None:
                value = normalized
        self.data[key] = value

    def __delitem__(self, key: str) -> None:
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)


def as_lap_record(record: LapRecord | Mapping[str, Any]) -> LapRecord:
    if isinstance(record, LapRecord):
        return record
    return LapRecord.from_dict(record)
