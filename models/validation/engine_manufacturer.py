from dataclasses import dataclass
from dataclasses import field
from typing import Any

from models.domain_utils.normalization import normalize_link_items
from models.domain_utils.normalization import (
    normalize_season_items as core_normalize_season_items,
)
from models.records.engine_manufacturer import ENGINE_MANUFACTURER_SCHEMA
from models.validation.base import ValidatedModel
from models.validation.constants import ALLOWED_MANUFACTURER_STATUSES
from models.validation.helpers import validate_status
from models.validation.utils import coerce_number
from models.value_objects.link import Link
from models.value_objects.season_ref import SeasonRef


@dataclass
class EngineManufacturer(ValidatedModel):
    __schema__ = ENGINE_MANUFACTURER_SCHEMA
    manufacturer: Link | dict[str, Any]
    manufacturer_status: str
    engines_built_in: list[Link | dict[str, Any]] = field(default_factory=list)
    seasons: list[SeasonRef | dict[str, Any]] = field(default_factory=list)
    races_entered: int | None = None
    races_started: int | None = None
    wins: int | None = None
    points: float | None = None
    poles: int | None = None
    fastest_laps: int | None = None
    podiums: int | None = None
    wcc: int | None = None
    wdc: int | None = None

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
            Link.from_dict(item)
            for item in normalize_link_items(
                self.engines_built_in,
                field_name="engines_built_in",
            )
        ]

        # --- seasons: koercja do SeasonRef + filtr None ---
        self.seasons = list(core_normalize_season_items(self.seasons))

        # --- stats ---
        self.races_entered = coerce_number(
            self.races_entered,
            int,
            "races_entered",
            allow_none=True,
        )
        self.races_started = coerce_number(
            self.races_started,
            int,
            "races_started",
            allow_none=True,
        )
        self.wins = coerce_number(self.wins, int, "wins", allow_none=True)
        self.points = coerce_number(self.points, float, "points", allow_none=True)
        self.poles = coerce_number(self.poles, int, "poles", allow_none=True)
        self.fastest_laps = coerce_number(
            self.fastest_laps,
            int,
            "fastest_laps",
            allow_none=True,
        )
        self.podiums = coerce_number(self.podiums, int, "podiums", allow_none=True)
        self.wcc = coerce_number(self.wcc, int, "wcc", allow_none=True)
        self.wdc = coerce_number(self.wdc, int, "wdc", allow_none=True)
