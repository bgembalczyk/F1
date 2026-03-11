from dataclasses import dataclass, field
from typing import Any, List, Optional

from models.validation.base import ValidatedModel
from models.validation.constants import ALLOWED_CIRCUIT_STATUSES
from models.validation.core import validate_float, validate_int, validate_status
from models.validation.validators import normalize_link_list, normalize_season_list
from models.value_objects.link import Link
from models.value_objects.season_ref import SeasonRef


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
        self.circuit = (
            self.circuit
            if isinstance(self.circuit, Link)
            else Link.from_dict(self.circuit)
        )

        # --- status + proste pola liczbowe ---
        self.circuit_status = validate_status(
            self.circuit_status,
            ALLOWED_CIRCUIT_STATUSES,
            "circuit_status",
        )
        self.last_length_used_km = validate_float(
            self.last_length_used_km, "last_length_used_km",
        )
        self.last_length_used_mi = validate_float(
            self.last_length_used_mi, "last_length_used_mi",
        )
        self.turns = validate_int(self.turns, "turns")
        self.grands_prix_held = validate_int(self.grands_prix_held, "grands_prix_held")

        # --- grands_prix: koercja do Link + filtr pustych ---
        self.grands_prix = normalize_link_list(self.grands_prix)

        # --- seasons: koercja do SeasonRef + filtr None ---
        self.seasons = normalize_season_list(self.seasons)
