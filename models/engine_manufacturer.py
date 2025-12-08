from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models.validators import (
    validate_float,
    validate_int,
    validate_link,
    validate_links,
    validate_seasons,
)


@dataclass
class EngineManufacturer:
    manufacturer: Dict[str, Optional[str]]
    manufacturer_status: str
    engines_built_in: List[Dict[str, Optional[str]]] = field(default_factory=list)
    seasons: List[Dict[str, Any]] = field(default_factory=list)
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
        self.manufacturer = validate_link(self.manufacturer, field_name="manufacturer")
        self.manufacturer_status = self._validate_status(self.manufacturer_status)
        self.engines_built_in = validate_links(
            self.engines_built_in, field_name="engines_built_in"
        )
        self.seasons = validate_seasons(self.seasons)
        self.races_entered = validate_int(self.races_entered, "races_entered")
        self.races_started = validate_int(self.races_started, "races_started")
        self.wins = validate_int(self.wins, "wins")
        self.points = validate_float(self.points, "points")
        self.poles = validate_int(self.poles, "poles")
        self.fastest_laps = validate_int(self.fastest_laps, "fastest_laps")
        self.podiums = validate_int(self.podiums, "podiums")
        self.wcc = validate_int(self.wcc, "wcc")
        self.wdc = validate_int(self.wdc, "wdc")

    @staticmethod
    def _validate_status(status: str) -> str:
        status_normalized = (status or "").strip().lower()
        allowed = {"current", "former"}
        if status_normalized not in allowed:
            raise ValueError("manufacturer_status musi być current lub former")
        return status_normalized
