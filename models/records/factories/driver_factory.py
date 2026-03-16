from collections.abc import Mapping
from typing import Any
from typing import cast

from models.mappers.field_aliases import FIELD_ALIASES
from models.records.base_factory import BaseRecordFactory
from models.records.driver import DriverRecord
from models.records.factories.drivers_championships_factory import (
    DriversChampionshipsRecordFactory,
)


class DriverRecordFactory(BaseRecordFactory):
    def __init__(self, normalizer=None):
        super().__init__(normalizer)
        self.championships_factory = DriversChampionshipsRecordFactory(self.normalizer)

    def build(self, record: Mapping[str, Any]) -> DriverRecord:
        payload = self.apply_aliases(record, FIELD_ALIASES["driver"], "driver")
        self.normalize_link_fields(payload, ["driver"])
        self.normalize_string_field(payload, "nationality")
        self.normalize_seasons_fields(payload, ["seasons_competed"])

        championships = payload.get("drivers_championships") or {}
        if isinstance(championships, Mapping):
            payload["drivers_championships"] = self.championships_factory.build(
                championships,
            )

        payload["is_active"] = self.normalizer.normalize_bool(payload.get("is_active"))
        payload["is_world_champion"] = self.normalizer.normalize_bool(
            payload.get("is_world_champion"),
        )
        self.normalize_int_fields(
            payload,
            [
                "race_entries",
                "race_starts",
                "pole_positions",
                "race_wins",
                "podiums",
                "fastest_laps",
            ],
        )
        self.set_defaults(
            payload,
            {
                "drivers_championships": {"count": 0, "seasons": []},
                "seasons_competed": [],
            },
        )
        return cast("DriverRecord", payload)
