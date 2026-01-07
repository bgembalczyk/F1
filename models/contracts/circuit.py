from dataclasses import dataclass, field
from typing import Any, Mapping

from models.contracts.base import DataContract
from models.records.link import LinkRecord
from models.records.season import SeasonRecord


@dataclass(slots=True)
class CircuitContract(DataContract):
    circuit: LinkRecord | None = None
    circuit_status: str | None = None
    type: str | None = None
    direction: str | None = None
    location: str | None = None
    country: str | None = None
    last_length_used_km: float | None = None
    last_length_used_mi: float | None = None
    turns: int | None = None
    grands_prix: list[LinkRecord] = field(default_factory=list)
    seasons: list[SeasonRecord] = field(default_factory=list)
    grands_prix_held: int | None = None

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "CircuitContract":
        payload = dict(record)
        payload.setdefault("grands_prix", [])
        payload.setdefault("seasons", [])
        return super(CircuitContract, cls).from_record(payload)
