from collections.abc import Iterable
from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from models.value_objects.normalized_date import NormalizedDate
from scrapers.base.helpers.value_objects.normalized_time import NormalizedTime


@dataclass
class LapRecord:
    data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        time_val = self.data.get("time")
        if isinstance(time_val, Mapping | NormalizedTime):
            normalized = NormalizedTime.from_value(time_val)
            if normalized is not None:
                self.data["time"] = normalized

        date_val = self.data.get("date")
        if isinstance(date_val, Mapping | NormalizedDate):
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
            if isinstance(value, NormalizedTime | NormalizedDate) or (
                hasattr(value, "to_dict") and callable(value.to_dict)
            ):
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
