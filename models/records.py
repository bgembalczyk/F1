from typing import Any, NotRequired, TypedDict


class LinkRecord(TypedDict):
    text: str
    url: str | None


class SeasonRecord(TypedDict):
    year: int
    url: str


class DriversChampionshipsRecord(TypedDict):
    count: int
    seasons: list[SeasonRecord]


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


class CircuitRecord(TypedDict):
    circuit: LinkRecord
    circuit_status: str
    type: str | None
    direction: str | None
    location: str | None
    country: str | None
    last_length_used_km: float | None
    last_length_used_mi: float | None
    turns: int | None
    grands_prix: list[LinkRecord]
    seasons: list[SeasonRecord]
    grands_prix_held: int | None


class CircuitDetailsRecord(TypedDict):
    url: str
    infobox: dict[str, Any]
    tables: list[dict[str, Any]]


class CircuitCompleteRecord(TypedDict, total=False):
    name: dict[str, Any]
    url: str | None
    circuit_status: str
    type: str | None
    direction: str | None
    grands_prix: list[LinkRecord]
    seasons: list[SeasonRecord]
    grands_prix_held: int | None
    location: dict[str, Any]
    fia_grade: str
    history: list[Any]
    layouts: list[dict[str, Any]]
