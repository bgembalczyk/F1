from dataclasses import dataclass, field
from typing import Any, Mapping

from models.contracts.base import DataContract
from models.records.driver_championships import DriversChampionshipsRecord
from models.records.link import LinkRecord
from models.records.season import SeasonRecord


@dataclass(slots=True)
class DriverContract(DataContract):
    driver: LinkRecord | None = None
    is_active: bool = False
    is_world_champion: bool = False
    nationality: str | None = None
    seasons_competed: list[SeasonRecord] = field(default_factory=list)
    drivers_championships: DriversChampionshipsRecord | str | None = field(
        default_factory=lambda: {"count": 0, "seasons": []}
    )
    race_entries: int | None = None
    race_starts: int | None = None
    pole_positions: int | None = None
    race_wins: int | None = None
    podiums: int | None = None
    fastest_laps: int | None = None
    points: str | None = None

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "DriverContract":
        payload = dict(record)
        payload.setdefault("seasons_competed", [])
        payload.setdefault("drivers_championships", {"count": 0, "seasons": []})
        return super().from_record(payload)
