from dataclasses import dataclass
from typing import Any

from scrapers.mappers.domain_mapper_abc import DomainMapperABC


@dataclass(frozen=True)
class IdentityDomainMapper(DomainMapperABC):
    """Domyślny mapper: brak mapowania."""

    def map(self, payload: dict[str, Any]) -> dict[str, Any]:
        return payload
