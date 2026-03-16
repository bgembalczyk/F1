from dataclasses import dataclass
from dataclasses import field
from typing import Any

from models.validation.base import ValidatedModel
from models.validation.constants import ALLOWED_CIRCUIT_STATUSES
from models.validation.core import validate_float
from models.validation.core import validate_int
from models.validation.core import validate_status
from models.validation.validators import normalize_season_list
from models.domain_utils.normalization import normalize_link_items
from models.value_objects.link import Link
from models.value_objects.season_ref import SeasonRef


@dataclass
class Circuit(ValidatedModel):
    circuit: Link | dict[str, Any]
    circuit_status: str
    type: str | None = None
    direction: str | None = None
    location: str | None = None
    country: str | None = None
    last_length_used_km: float | None = None
    last_length_used_mi: float | None = None
    turns: int | None = None
    grands_prix: list[Link | dict[str, Any]] = field(default_factory=list)
    seasons: list[SeasonRef | dict[str, Any]] = field(default_factory=list)
    grands_prix_held: int | None = None

    def __post_init__(self) -> None:
        # Ten hook gwarantuje walidację.
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
            self.last_length_used_km,
            "last_length_used_km",
        )
        self.last_length_used_mi = validate_float(
            self.last_length_used_mi,
            "last_length_used_mi",
        )
        self.turns = validate_int(self.turns, "turns")
        self.grands_prix_held = validate_int(
            self.grands_prix_held,
            "grands_prix_held",
        )

        # --- grands_prix: koercja do Link + filtr pustych ---
        self.grands_prix = [Link.from_dict(item) for item in normalize_link_items(self.grands_prix, field_name="grands_prix")]

        # --- seasons: koercja do SeasonRef + filtr None ---
        self.seasons = normalize_season_list(self.seasons)
