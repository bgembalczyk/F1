from collections.abc import Mapping
from typing import Any
from typing import cast

from models.mappers.field_aliases import FIELD_ALIASES
from models.records.base_factory import BaseRecordFactory
from models.records.driver import DriverRecord
from models.records.factories.drivers_championships_factory import (
    DriversChampionshipsRecordFactory,
)
from models.records.factories.registry import register_factory


@register_factory("driver")
class DriverRecordFactory(BaseRecordFactory):
    record_type = "driver"

    def __init__(self, normalizer=None):
        super().__init__(normalizer)
        self.championships_factory = DriversChampionshipsRecordFactory(self.normalizer)

    def build(self, record: Mapping[str, Any]) -> DriverRecord:
        payload = self.apply_spec(
            record,
            {
                "aliases": FIELD_ALIASES["driver"],
                "record_name": "driver",
                "field_normalizers": {
                    "nationality": lambda value, _field: (
                        self.normalizer.normalize_string(
                            value,
                        )
                    ),
                    "is_active": lambda value, _field: bool(value),
                    "is_world_champion": lambda value, _field: bool(value),
                },
                "list_field_normalizers": {
                    "link": ["driver"],
                    "seasons": ["seasons_competed"],
                    "int": [
                        "race_entries",
                        "race_starts",
                        "pole_positions",
                        "race_wins",
                        "podiums",
                        "fastest_laps",
                    ],
                },
                "nested_factories": {
                    "drivers_championships": self.championships_factory,
                },
                "defaults": {
                    "drivers_championships": {"count": 0, "seasons": []},
                    "seasons_competed": [],
                    "race_entries": None,
                    "race_starts": None,
                    "pole_positions": None,
                    "race_wins": None,
                    "podiums": None,
                    "fastest_laps": None,
                },
            },
        )
        return cast("DriverRecord", payload)
