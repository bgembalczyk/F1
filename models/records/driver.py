from typing import Optional, TypedDict

from models.records.driver_championships import DriversChampionshipsRecord
from models.records.link import LinkRecord
from models.records.season import SeasonRecord


class DriverRecord(TypedDict, total=False):
    driver: LinkRecord
    is_active: bool
    is_world_champion: bool
    nationality: Optional[str]
    seasons_competed: list[SeasonRecord]
    drivers_championships: DriversChampionshipsRecord
    race_entries: Optional[int]
    race_starts: Optional[int]
    pole_positions: Optional[int]
    race_wins: Optional[int]
    podiums: Optional[int]
    fastest_laps: Optional[int]
    points: Optional[str]
