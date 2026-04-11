from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import runtime_checkable

if False:  # pragma: no cover
    from bs4 import BeautifulSoup


@runtime_checkable
class ListScraperContract(Protocol):
    """Minimal contract for list/seed scrapers."""

    def fetch(self) -> list[dict[str, Any]]: ...


@runtime_checkable
class TableScraperContract(Protocol):
    """Minimal contract for table-based scrapers."""

    def parse_soup(self, soup: BeautifulSoup) -> list[Any]: ...

    def parse_row(self, row: Any) -> Any | None: ...


@runtime_checkable
class SingleArticleScraperContract(Protocol):
    """Minimal contract for single-article scrapers."""

    def extract_by_url(self, url: str) -> list[dict[str, Any]]: ...

    def _assemble_record(self, **kwargs: Any) -> dict[str, Any]: ...


__all__ = [
    "ListScraperContract",
    "TableScraperContract",
    "SingleArticleScraperContract",
]
