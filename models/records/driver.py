from typing import NotRequired
from typing import TypedDict

from models.records.driver_championships import DriversChampionshipsRecord
from models.records.link import LinkRecord
from models.records.season import SeasonRecord


class DriverRecord(TypedDict):
    driver: LinkRecord
    is_active: bool
    is_world_champion: bool
    nationality: str
    seasons_competed: list[SeasonRecord]
    drivers_championships: DriversChampionshipsRecord
    race_entries: NotRequired[int | None]
    race_starts: NotRequired[int | None]
    pole_positions: NotRequired[int | None]
    race_wins: NotRequired[int | None]
    podiums: NotRequired[int | None]
    fastest_laps: NotRequired[int | None]
    points: NotRequired[str | None]
