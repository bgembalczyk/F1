from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from models.contracts.base import DataContract
from models.records.season import SeasonRecord

POINTS_KEYS = {
    "1st",
    "2nd",
    "3rd",
    "4th",
    "5th",
    "6th",
    "7th",
    "8th",
    "9th",
    "10th",
    "fastest_lap",
    "drivers_championship",
    "constructors_championship",
    "race_length_completed",
    "race_length_points",
}


@dataclass(slots=True)
class PointsContract(DataContract):
    seasons: list[SeasonRecord] = field(default_factory=list)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "PointsContract":
        payload = dict(record)
        payload.setdefault("seasons", [])
        return super(PointsContract, cls).from_record(payload)
