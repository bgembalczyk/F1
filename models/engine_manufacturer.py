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
class EngineManufacturer(ValidatedModel):
    manufacturer: Link
    manufacturer_status: str
    engines_built_in: List[Link] = field(default_factory=list)
    seasons: List[SeasonRef] = field(default_factory=list)
    races_entered: Optional[int] = None
    races_started: Optional[int] = None
    wins: Optional[int] = None
    points: Optional[float] = None
    poles: Optional[int] = None
    fastest_laps: Optional[int] = None
    podiums: Optional[int] = None
    wcc: Optional[int] = None
    wdc: Optional[int] = None

    def validate(self) -> None:
        # --- manufacturer ---
        self.manufacturer = Link.from_dict(
            validate_link(self.manufacturer.to_dict(), field_name="manufacturer")
        )

        self.manufacturer_status = validate_status(
            self.manufacturer_status,
            {"current", "former"},
            "manufacturer_status",
        )

        # --- engines_built_in ---
        engines_dicts = [e.to_dict() for e in self.engines_built_in]
        engines_validated = validate_links(
            engines_dicts, field_name="engines_built_in"
        )
        self.engines_built_in = [
            Link.from_dict(d)
            for d in engines_validated
            if not Link.from_dict(d).is_empty()
        ]

        # --- seasons ---
        seasons_dicts = [s.to_dict() for s in self.seasons]
        seasons_validated = validate_seasons(seasons_dicts)
        self.seasons = [
            SeasonRef.from_dict(d)
            for d in seasons_validated
            if d is not None
        ]

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
