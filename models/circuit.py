from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models.validators import (
    validate_float,
    validate_int,
    validate_link,
    validate_links,
)
from models.validators import validate_seasons


@dataclass
class Circuit:
    circuit: Dict[str, Optional[str]]
    circuit_status: str
    type: Optional[str] = None
    direction: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    last_length_used_km: Optional[float] = None
    last_length_used_mi: Optional[float] = None
    turns: Optional[int] = None
    grands_prix: List[Dict[str, Optional[str]]] = field(default_factory=list)
    seasons: List[Dict[str, Any]] = field(default_factory=list)
    grands_prix_held: Optional[int] = None

    def __post_init__(self) -> None:
        self.circuit = validate_link(self.circuit, field_name="circuit")
        self.circuit_status = self._validate_status(self.circuit_status)
        self.last_length_used_km = validate_float(
            self.last_length_used_km, "last_length_used_km"
        )
        self.last_length_used_mi = validate_float(
            self.last_length_used_mi, "last_length_used_mi"
        )
        self.turns = validate_int(self.turns, "turns")
        self.grands_prix = validate_links(self.grands_prix, field_name="grands_prix")
        self.grands_prix_held = validate_int(self.grands_prix_held, "grands_prix_held")
        self.seasons = validate_seasons(self.seasons)

    @staticmethod
    def _validate_status(status: str) -> str:
        status_normalized = (status or "").strip().lower()
        allowed = {"current", "future", "former"}
        if status_normalized not in allowed:
            raise ValueError(
                "circuit_status musi być jedną z wartości current/future/former"
            )
        return status_normalized
