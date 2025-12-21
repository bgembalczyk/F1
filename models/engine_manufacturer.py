from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from models.base import ValidatedModel
from models.constants import ALLOWED_MANUFACTURER_STATUSES
from models.value_objects import Link, SeasonRef
from models.validators import (
    validate_float,
    validate_int,
    validate_status,
)


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
        self.engines_built_in = [
            (item if isinstance(item, Link) else Link.from_dict(item))
            for item in (self.engines_built_in or [])
        ]
        self.engines_built_in = [
            link for link in self.engines_built_in if not link.is_empty()
        ]

        # --- seasons: koercja do SeasonRef + filtr None ---
        normalized_seasons: list[SeasonRef] = []
        for item in (self.seasons or []):
            season = item if isinstance(item, SeasonRef) else SeasonRef.from_dict(item)
            if season is not None:
                normalized_seasons.append(season)
        self.seasons = normalized_seasons

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
