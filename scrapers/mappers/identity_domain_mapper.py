from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IdentityDomainMapper:
    """Domyślny mapper: brak mapowania."""

    def map(self, payload: dict[str, Any]) -> dict[str, Any]:
        return payload
