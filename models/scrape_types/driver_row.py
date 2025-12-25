from typing import Optional
from typing import TypedDict

from models.records.link import LinkRecord
from models.scrape_types.driver_championships_payload import DriverChampionshipsPayload
from models.scrape_types.season_ref_payload import SeasonRefPayload


class DriverRow(TypedDict, total=False):
    driver: LinkRecord
    is_active: bool
    is_world_champion: bool
    nationality: Optional[str]
    seasons_competed: list[SeasonRefPayload]
    drivers_championships: DriverChampionshipsPayload
    race_entries: Optional[int]
    race_starts: Optional[int]
    pole_positions: Optional[int]
    race_wins: Optional[int]
    podiums: Optional[int]
    fastest_laps: Optional[int]
    points: Optional[str]
