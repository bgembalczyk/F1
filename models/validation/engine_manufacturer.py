from dataclasses import dataclass
from dataclasses import field
from typing import Any

from models.domain_utils.normalization import normalize_link_items
from models.records.engine_manufacturer import ENGINE_MANUFACTURER_SCHEMA
from models.validation.base import ValidatedModel
from models.validation.constants import ALLOWED_MANUFACTURER_STATUSES
from models.validation.helpers import validate_float
from models.validation.helpers import validate_int
from models.validation.helpers import validate_status
from models.validation.validators import normalize_season_list
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
