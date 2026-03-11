from dataclasses import asdict, is_dataclass
from typing import Any, Mapping, TypeVar

TValueObject = TypeVar("TValueObject", bound="ValueObject")


class ValueObject:
    def to_dict(self) -> dict[str, Any]:
        if is_dataclass(self):
            return asdict(self)
        raise TypeError(f"Nieobsługiwany ValueObject: {type(self)!r}")

    @classmethod
    def from_dict(
            cls: type[TValueObject],
            data: Mapping[str, Any] | TValueObject | None,
    ) -> TValueObject | None:
        if data is None:
            return None
        if isinstance(data, cls):
            return data
        if not isinstance(data, Mapping):
            raise TypeError(f"Nieobsługiwany typ danych: {type(data)!r}")
        return cls(**dict(data))  # type: ignore[arg-type]
