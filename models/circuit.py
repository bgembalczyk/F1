from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from models.constants import ALLOWED_CIRCUIT_STATUSES
from models.value_objects import Link, SeasonRef
from models.validators import (
    validate_float,
    validate_int,
    validate_status,
)


@dataclass
class Circuit:
    circuit: Link
    circuit_status: str
    type: Optional[str] = None
    direction: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    last_length_used_km: Optional[float] = None
    last_length_used_mi: Optional[float] = None
    turns: Optional[int] = None
    grands_prix: List[Link] = field(default_factory=list)
    seasons: List[SeasonRef] = field(default_factory=list)
    grands_prix_held: Optional[int] = None

    def __post_init__(self) -> None:
        self.circuit = (
            self.circuit
            if isinstance(self.circuit, Link)
            else Link.from_dict(self.circuit)
        )
        self.circuit_status = validate_status(
            self.circuit_status,
            ALLOWED_CIRCUIT_STATUSES,
            "circuit_status",
        )
        self.last_length_used_km = validate_float(
            self.last_length_used_km, "last_length_used_km"
        )
        self.last_length_used_mi = validate_float(
            self.last_length_used_mi, "last_length_used_mi"
        )
        self.turns = validate_int(self.turns, "turns")
        self.grands_prix = [
            link
            for link in (
                item if isinstance(item, Link) else Link.from_dict(item)
                for item in self.grands_prix
            )
            if not link.is_empty()
        ]
        self.grands_prix_held = validate_int(self.grands_prix_held, "grands_prix_held")
        self.seasons = [
            season
            for season in (
                item if isinstance(item, SeasonRef) else SeasonRef.from_dict(item)
                for item in self.seasons
            )
            if season is not None
        ]
