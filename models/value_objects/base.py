from abc import ABC
from abc import abstractmethod
from collections.abc import Mapping
from dataclasses import asdict
from dataclasses import is_dataclass
from typing import Any

from typing_extensions import Self


class ValueObject(ABC):
    def to_dict(self) -> dict[str, Any]:
        """Kontrakt serializacji między warstwą domenową a mapperami."""
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
        try:
            return cls.from_mapping(data)
        except (TypeError, ValueError, KeyError) as exc:
            msg = f"Nie można utworzyć {cls.__name__} z przekazanego payloadu: {exc}"
            raise ValueError(msg) from exc

    @classmethod
    @abstractmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> Self | None:
        """Build a value object from mapping payload."""
