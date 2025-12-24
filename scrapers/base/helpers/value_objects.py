from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_seconds(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return float(stripped)
        except ValueError:
            return None
    return None


def _normalize_iso(value: Any) -> str | None:
    if isinstance(value, list):
        value = value[0] if value else None
    return _normalize_text(value)


@dataclass(frozen=True)
class NormalizedTime:
    text: str | None = None
    seconds: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", _normalize_text(self.text))
        object.__setattr__(self, "seconds", _normalize_seconds(self.seconds))

    @classmethod
    def from_value(cls, value: Any):
        if value is None:
            return None
        if isinstance(value, NormalizedTime):
            return value
        if isinstance(value, Mapping):
            return cls(text=value.get("text"), seconds=value.get("seconds"))
        if isinstance(value, (int, float)):
            return cls(text=None, seconds=float(value))
        return cls(text=str(value).strip(), seconds=None)

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "seconds": self.seconds}


@dataclass(frozen=True)
class NormalizedDate:
    text: str | None = None
    iso: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", _normalize_text(self.text))
        object.__setattr__(self, "iso", _normalize_iso(self.iso))

    @classmethod
    def from_value(cls, value: Any):
        if value is None:
            return None
        if isinstance(value, NormalizedDate):
            return value
        if isinstance(value, Mapping):
            return cls(text=value.get("text"), iso=value.get("iso"))
        if isinstance(value, str):
            return cls(text=value, iso=None)
        return cls(text=str(value).strip(), iso=None)

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "iso": self.iso}


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

        date_val = self.data.get("date")
        if isinstance(date_val, Mapping) or isinstance(date_val, NormalizedDate):
            normalized = NormalizedDate.from_value(date_val)
            if normalized is not None:
                self.data["date"] = normalized

        if "class" in self.data and "class_" not in self.data:
            self.data["class_"] = self.data.get("class")

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]):
        return cls(data=dict(payload))

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in self.data.items():
            if isinstance(value, NormalizedTime):
                result[key] = value.to_dict()
            elif isinstance(value, NormalizedDate):
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
        if key == "date" and not isinstance(value, NormalizedDate):
            normalized = NormalizedDate.from_value(value)
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
