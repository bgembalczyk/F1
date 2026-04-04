from dataclasses import dataclass
from dataclasses import field
from typing import Any

from models.domain_utils.normalization import normalize_link_items
from models.domain_utils.normalization import (
    normalize_season_items as core_normalize_season_items,
)
from models.records.circuit import CIRCUIT_SCHEMA
from models.validation.base import ValidatedModel
from models.validation.constants import ALLOWED_CIRCUIT_STATUSES
from models.validation.helpers import validate_status
from models.validation.utils import coerce_number
from models.value_objects.link import Link
from models.value_objects.season_ref import SeasonRef


@dataclass
class Circuit(ValidatedModel):
    __schema__ = CIRCUIT_SCHEMA
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
        self.last_length_used_km = coerce_number(
            self.last_length_used_km,
            float,
            "last_length_used_km",
            allow_none=True,
        )
        self.last_length_used_mi = coerce_number(
            self.last_length_used_mi,
            float,
            "last_length_used_mi",
            allow_none=True,
        )
        self.turns = coerce_number(self.turns, int, "turns", allow_none=True)
        self.grands_prix_held = coerce_number(
            self.grands_prix_held,
            int,
            "grands_prix_held",
            allow_none=True,
        )

        # --- grands_prix: koercja do Link + filtr pustych ---
        self.grands_prix = [
            Link.from_dict(item)
            for item in normalize_link_items(self.grands_prix, field_name="grands_prix")
        ]

        # --- seasons: koercja do SeasonRef + filtr None ---
        self.seasons = list(core_normalize_season_items(self.seasons))
