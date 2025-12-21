from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from models.base import ValidatedModel
from models.constants import ALLOWED_CIRCUIT_STATUSES
from models.value_objects import Link, SeasonRef
from models.validators import (
    validate_float,
    validate_int,
    validate_status,
)


@dataclass
class Circuit(ValidatedModel):
    circuit: Link | dict[str, Any]
    circuit_status: str
    type: Optional[str] = None
    direction: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    last_length_used_km: Optional[float] = None
    last_length_used_mi: Optional[float] = None
    turns: Optional[int] = None
    grands_prix: List[Link | dict[str, Any]] = field(default_factory=list)
    seasons: List[SeasonRef | dict[str, Any]] = field(default_factory=list)
    grands_prix_held: Optional[int] = None

    def __post_init__(self) -> None:
        # Jeśli ValidatedModel nie robi tego automatycznie, to ten hook gwarantuje walidację
        self.validate()

    def validate(self) -> None:
        # --- circuit ---
        self.circuit = self.circuit if isinstance(self.circuit, Link) else Link.from_dict(self.circuit)

        # --- status + proste pola liczbowe ---
        self.circuit_status = validate_status(
            self.circuit_status,
            ALLOWED_CIRCUIT_STATUSES,
            "circuit_status",
        )
        self.last_length_used_km = validate_float(self.last_length_used_km, "last_length_used_km")
        self.last_length_used_mi = validate_float(self.last_length_used_mi, "last_length_used_mi")
        self.turns = validate_int(self.turns, "turns")
        self.grands_prix_held = validate_int(self.grands_prix_held, "grands_prix_held")

        # --- grands_prix: koercja do Link + filtr pustych ---
        self.grands_prix = [
            (item if isinstance(item, Link) else Link.from_dict(item))
            for item in (self.grands_prix or [])
        ]
        self.grands_prix = [link for link in self.grands_prix if not link.is_empty()]

        # --- seasons: koercja do SeasonRef + filtr None ---
        normalized_seasons: list[SeasonRef] = []
        for item in (self.seasons or []):
            season = item if isinstance(item, SeasonRef) else SeasonRef.from_dict(item)
            if season is not None:
                normalized_seasons.append(season)
        self.seasons = normalized_seasons
