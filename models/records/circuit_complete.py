from typing import Any
from typing import TypedDict

from models.records.link import LinkRecord
from models.records.season import SeasonRecord


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
