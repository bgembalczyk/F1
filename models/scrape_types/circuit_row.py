from typing import Literal
from typing import Optional
from typing import TypedDict

from models.records.link import LinkRecord
from models.scrape_types.season_ref_payload import SeasonRefPayload


class CircuitRow(TypedDict, total=False):
    circuit: LinkRecord
    circuit_status: Literal["current", "future", "former"]
    type: Optional[str]
    direction: Optional[str]
    location: Optional[str]
    country: Optional[str]
    last_length_used_km: Optional[float]
    last_length_used_mi: Optional[float]
    turns: Optional[int]
    grands_prix: list[LinkRecord]
    seasons: list[SeasonRefPayload]
    grands_prix_held: Optional[int]
