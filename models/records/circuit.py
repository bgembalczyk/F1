from typing import TypedDict

from models.records.link import LinkRecord
from models.records.season import SeasonRecord


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
