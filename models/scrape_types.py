from typing import Literal, Optional, TypeAlias, TypedDict

from models.records import LinkRecord


LinkPayload: TypeAlias = LinkRecord


class SeasonRefPayload(TypedDict):
    year: int
    url: Optional[str]


class DriverChampionshipsPayload(TypedDict):
    count: int
    seasons: list[SeasonRefPayload]


class DriverRow(TypedDict, total=False):
    driver: LinkPayload
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


class ConstructorRow(TypedDict, total=False):
    constructor: LinkPayload
    engine: list[LinkPayload]
    licensed_in: Optional[str | LinkPayload | list[LinkPayload]]
    based_in: list[LinkPayload]
    team: str
    team_url: Optional[str]
    seasons: list[SeasonRefPayload]
    races_entered: Optional[int]
    races_started: Optional[int]
    drivers: Optional[int]
    total_entries: Optional[int]
    wins: Optional[int]
    points: Optional[int]
    poles: Optional[int]
    fastest_laps: Optional[int]
    podiums: Optional[int]
    wcc_titles: Optional[int]
    wdc_titles: Optional[int]
    antecedent_teams: list[LinkPayload]


class CircuitRow(TypedDict, total=False):
    circuit: LinkPayload
    circuit_status: Literal["current", "future", "former"]
    type: Optional[str]
    direction: Optional[str]
    location: Optional[str]
    country: Optional[str]
    last_length_used_km: Optional[float]
    last_length_used_mi: Optional[float]
    turns: Optional[int]
    grands_prix: list[LinkPayload]
    seasons: list[SeasonRefPayload]
    grands_prix_held: Optional[int]
