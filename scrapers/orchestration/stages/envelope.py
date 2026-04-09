from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass(frozen=True)
class StageEnvelope:
    """Minimalny kontrakt danych przekazywany pomiędzy etapami."""

    domain: str
    stage: str
    records: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

