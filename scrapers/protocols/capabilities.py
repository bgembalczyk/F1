from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol

from validation.validator_base import ExportRecord

if TYPE_CHECKING:
    from scrapers.results import ScrapeResult


class FetchCapability(Protocol):
    """Capability contract for data acquisition in scraper pipeline."""

    def fetch(self) -> list[ExportRecord]: ...


class ValidateCapability(Protocol):
    """Capability contract for record validation stage."""

    def validate_records(self, records: list[ExportRecord]) -> list[ExportRecord]: ...


class ExportCapability(Protocol):
    """Capability contract for formatting and persistence of scrape results."""

    def build_result(self, data: list[ExportRecord] | None = None) -> ScrapeResult: ...

    def to_json(
        self,
        path: str,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None: ...

    def to_csv(
        self,
        path: str,
        *,
        fieldnames: list[str] | None = None,
        fieldnames_strategy: str = "union",
        include_metadata: bool = False,
    ) -> None: ...
