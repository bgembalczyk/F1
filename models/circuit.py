from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from models.base import ValidatedModel
from models.value_objects import Link, SeasonRef
from models.validators import (
    validate_float,
    validate_int,
    validate_link,
    validate_links,
    validate_seasons,
    validate_status,
)


@dataclass
class Circuit(ValidatedModel):
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

    def validate(self) -> None:
        # Link -> dict -> validator -> Link
        self.circuit = Link.from_dict(validate_link(self.circuit.to_dict(), field_name="circuit"))

        self.circuit_status = validate_status(
            self.circuit_status,
            {"current", "future", "former"},
            "circuit_status",
        )

        self.last_length_used_km = validate_float(self.last_length_used_km, "last_length_used_km")
        self.last_length_used_mi = validate_float(self.last_length_used_mi, "last_length_used_mi")
        self.turns = validate_int(self.turns, "turns")
        self.grands_prix_held = validate_int(self.grands_prix_held, "grands_prix_held")

        # List[Link] -> List[dict] -> validator -> List[Link] + odfiltrowanie pustych
        gp_dicts = [gp.to_dict() for gp in self.grands_prix]
        gp_validated = validate_links(gp_dicts, field_name="grands_prix")
        self.grands_prix = [
            Link.from_dict(d) for d in gp_validated
            if not Link.from_dict(d).is_empty()
        ]

        # List[SeasonRef] -> List[dict] -> validator -> List[SeasonRef]
        seasons_dicts = [s.to_dict() for s in self.seasons]
        seasons_validated = validate_seasons(seasons_dicts)
        self.seasons = [
            SeasonRef.from_dict(d) for d in seasons_validated
            if d is not None
        ]
