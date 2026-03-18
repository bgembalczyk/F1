from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass(frozen=True)
class Rounds:
    values: tuple[int, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        normalized = self._normalize_values(self.values)
        object.__setattr__(self, "values", normalized)

    @classmethod
    def from_values(cls, values: Iterable[int] | None) -> "Rounds":
        return cls(tuple(values or ()))

    @staticmethod
    def _normalize_values(values: Iterable[Any]) -> tuple[int, ...]:
        normalized: list[int] = []
        seen: set[int] = set()
        for value in values:
            try:
                round_no = int(value)
            except (TypeError, ValueError) as exc:
                msg = "Numery rund muszą być liczbami całkowitymi"
                raise ValueError(msg) from exc
            if round_no <= 0:
                msg = "Numery rund muszą być dodatnie"
                raise ValueError(msg)
            if round_no in seen:
                continue
            seen.add(round_no)
            normalized.append(round_no)
        normalized.sort()
        return tuple(normalized)

    def to_list(self) -> list[int]:
        return list(self.values)

    def __bool__(self) -> bool:
        return bool(self.values)

    def __iter__(self):
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def __getitem__(self, index: int) -> int:
        return self.values[index]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Rounds):
            return self.values == other.values
        if isinstance(other, list | tuple):
            return list(self.values) == list(other)
        return NotImplemented
