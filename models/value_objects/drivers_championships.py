from collections.abc import Iterable
from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from models.value_objects.base import ValueObject
from models.value_objects.season_ref import SeasonRef


@dataclass
class DriversChampionships(ValueObject):
    count: int = 0
    seasons: list[SeasonRef] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.count = self._normalize_count(self.count)
        self.seasons = self._normalize_seasons(self.seasons)
        if self.count == 0 and self.seasons:
            msg = "Liczba tytułów nie może wynosić 0, gdy lista sezonów nie jest pusta"
            raise ValueError(msg)
        if self.seasons and self.count != len(self.seasons):
            msg = "Liczba tytułów musi odpowiadać liczbie sezonów mistrzowskich"
            raise ValueError(msg)

    @staticmethod
    def _normalize_count(value: Any) -> int:
        try:
            count = int(value)
        except (TypeError, ValueError) as exc:
            msg = "Pole count musi być liczbą całkowitą"
            raise ValueError(msg) from exc
        if count < 0:
            msg = "Pole count nie może być ujemne"
            raise ValueError(msg)
        return count

    @staticmethod
    def _normalize_seasons(
        values: Iterable[SeasonRef | Mapping[str, Any] | None],
    ) -> list[SeasonRef]:
        seasons: list[SeasonRef] = []
        seen_years: set[int] = set()
        for value in values:
            season = SeasonRef.from_dict(value)
            if season is None:
                continue
            if season.year in seen_years:
                msg = f"Sezon mistrzowski {season.year} występuje więcej niż raz"
                raise ValueError(msg)
            seen_years.add(season.year)
            seasons.append(season)
        return seasons

    @classmethod
    def from_value(
        cls,
        value: "DriversChampionships | Mapping[str, Any] | None",
    ) -> "DriversChampionships":
        if isinstance(value, cls):
            return value
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            msg = f"Nieobsługiwany typ danych: {type(value)!r}"
            raise TypeError(msg)
        return cls.from_mapping(value)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "DriversChampionships":
        payload = dict(data)
        return cls(count=payload.get("count", 0), seasons=payload.get("seasons") or [])

    def to_dict(self) -> dict[str, Any]:
        """Kontrakt eksportu osiągnięć kierowcy do rekordu domenowego."""
        return {
            "count": self.count,
            "seasons": [season.to_dict() for season in self.seasons],
        }
