from collections.abc import Mapping
from dataclasses import asdict
from dataclasses import is_dataclass
from typing import Any

from typing_extensions import Self


class ValueObject:
    def to_dict(self) -> dict[str, Any]:
        if is_dataclass(self):
            return asdict(self)
        msg = f"Nieobsługiwany ValueObject: {type(self)!r}"
        raise TypeError(msg)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any] | Self | None,
    ) -> Self | None:
        if data is None:
            return None
        if isinstance(data, cls):
            return data
        if not isinstance(data, Mapping):
            msg = f"Nieobsługiwany typ danych: {type(data)!r}"
            raise TypeError(msg)
        return cls(**dict(data))  # type: ignore[arg-type]
