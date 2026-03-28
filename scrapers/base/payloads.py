from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InfoboxPayload:
    """Typed wrapper for infobox payload passed between scraper hooks."""

    data: dict[str, Any] | list[dict[str, Any]]

    def to_export(self) -> dict[str, Any] | list[dict[str, Any]]:
        return self.data


@dataclass(frozen=True)
class TablesPayload:
    """Typed wrapper for tables payload passed between scraper hooks."""

    data: list[dict[str, Any]]

    def to_export(self) -> list[dict[str, Any]]:
        return self.data


@dataclass(frozen=True)
class SectionsPayload:
    """Typed wrapper for sections payload passed between scraper hooks."""

    data: list[dict[str, Any]]

    def to_export(self) -> list[dict[str, Any]]:
        return self.data
