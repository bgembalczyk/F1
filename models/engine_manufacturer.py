from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from models.value_objects import Link, SeasonRef
from models.validators import (
    validate_float,
    validate_int,
    validate_status,
)


@dataclass
class EngineManufacturer:
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

    def __post_init__(self) -> None:
        self.manufacturer = (
            self.manufacturer
            if isinstance(self.manufacturer, Link)
            else Link.from_dict(self.manufacturer)
        )
        self.manufacturer_status = validate_status(
            self.manufacturer_status,
            {"current", "former"},
            "manufacturer_status",
        )
        self.engines_built_in = [
            link
            for link in (
                item if isinstance(item, Link) else Link.from_dict(item)
                for item in self.engines_built_in
            )
            if not link.is_empty()
        ]
        self.seasons = [
            season
            for season in (
                item if isinstance(item, SeasonRef) else SeasonRef.from_dict(item)
                for item in self.seasons
            )
            if season is not None
        ]
        self.races_entered = validate_int(self.races_entered, "races_entered")
        self.races_started = validate_int(self.races_started, "races_started")
        self.wins = validate_int(self.wins, "wins")
        self.points = validate_float(self.points, "points")
        self.poles = validate_int(self.poles, "poles")
        self.fastest_laps = validate_int(self.fastest_laps, "fastest_laps")
        self.podiums = validate_int(self.podiums, "podiums")
        self.wcc = validate_int(self.wcc, "wcc")
        self.wdc = validate_int(self.wdc, "wdc")
