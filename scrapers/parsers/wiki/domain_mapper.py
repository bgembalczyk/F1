from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any


class DomainMapperABC(ABC):
    """Mapuje parsed payload wiki na rekordy domenowe."""

    @abstractmethod
    def map(self, payload: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class IdentityDomainMapper(DomainMapperABC):
    """Domyślny mapper: brak mapowania (parser sekcji nie mapuje domeny)."""

    def map(self, payload: dict[str, Any]) -> dict[str, Any]:
        return payload


def build_default_domain_mapper() -> DomainMapperABC:
    return IdentityDomainMapper()


__all__ = ["DomainMapperABC", "IdentityDomainMapper", "build_default_domain_mapper"]
