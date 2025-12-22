from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from models.validation.base import ValidatedModel
from models.validation.constants import ALLOWED_MANUFACTURER_STATUSES
from models.validation.validators import (
    validate_status,
    normalize_link_list,
    normalize_season_list,
    validate_int,
    validate_float,
)
from models.value_objects import Link, SeasonRef


@dataclass
class EngineManufacturer(ValidatedModel):
    manufacturer: Link | dict[str, Any]
    manufacturer_status: str
    engines_built_in: List[Link | dict[str, Any]] = field(default_factory=list)
    seasons: List[SeasonRef | dict[str, Any]] = field(default_factory=list)
    races_entered: Optional[int] = None
    races_started: Optional[int] = None
    wins: Optional[int] = None
    points: Optional[float] = None
    poles: Optional[int] = None
    fastest_laps: Optional[int] = None
    podiums: Optional[int] = None
    wcc: Optional[int] = None
    wdc: Optional[int] = None

    def __post_init__(self) -> None:
        # Jeśli ValidatedModel nie odpala walidacji sam, ten hook to wymusza
        self.validate()

    def validate(self) -> None:
        # --- manufacturer (Link | dict -> Link) ---
        self.manufacturer = (
            self.manufacturer
            if isinstance(self.manufacturer, Link)
            else Link.from_dict(self.manufacturer)
        )

        # --- status ---
        self.manufacturer_status = validate_status(
            self.manufacturer_status,
            ALLOWED_MANUFACTURER_STATUSES,
            "manufacturer_status",
        )

        # --- engines_built_in: koercja do Link + filtr pustych ---
        self.engines_built_in = normalize_link_list(self.engines_built_in)

        # --- seasons: koercja do SeasonRef + filtr None ---
        self.seasons = normalize_season_list(self.seasons)

        # --- stats ---
        self.races_entered = validate_int(self.races_entered, "races_entered")
        self.races_started = validate_int(self.races_started, "races_started")
        self.wins = validate_int(self.wins, "wins")
        self.points = validate_float(self.points, "points")
        self.poles = validate_int(self.poles, "poles")
        self.fastest_laps = validate_int(self.fastest_laps, "fastest_laps")
        self.podiums = validate_int(self.podiums, "podiums")
        self.wcc = validate_int(self.wcc, "wcc")
        self.wdc = validate_int(self.wdc, "wdc")
