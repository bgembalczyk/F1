from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol


class DomainMapper(Protocol):
    """Mapuje parsed payload wiki na rekordy domenowe."""

    def map(self, payload: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class IdentityDomainMapper:
    """Domyślny mapper: brak mapowania (parser sekcji nie mapuje domeny)."""

    def map(self, payload: dict[str, Any]) -> dict[str, Any]:
        return payload


def build_default_domain_mapper() -> DomainMapper:
    return IdentityDomainMapper()


__all__ = ["DomainMapper", "IdentityDomainMapper", "build_default_domain_mapper"]
