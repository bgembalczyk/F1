from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from collections.abc import Callable


class RecordAssemblyStrategy(ABC):
    """Jawnie typowana strategia składania rekordu listy i szczegółów."""

    @abstractmethod
    def assemble(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Zwróć rekord wynikowy zbudowany z danych listy i szczegółów."""


@dataclass(frozen=True)
class AttachDetailsStrategy(RecordAssemblyStrategy):
    details_key: str = "details"

    def assemble(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        assembled = dict(record)
        assembled[self.details_key] = details
        return assembled


@dataclass(frozen=True)
class ExtractDetailFieldStrategy(RecordAssemblyStrategy):
    detail_field: str
    target_key: str | None = None

    def assemble(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        assembled = dict(record)
        target_key = self.target_key or self.detail_field
        assembled[target_key] = (
            details.get(self.detail_field) if isinstance(details, dict) else None
        )
        return assembled


@dataclass(frozen=True)
class BundleRecordWithDetailsStrategy(RecordAssemblyStrategy):
    record_field: str
    details_key: str = "details"
    details_default: dict[str, Any] = field(default_factory=dict)

    def assemble(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        record_value = record.get(self.record_field)
        return {
            self.record_field: record_value if isinstance(record_value, dict) else {},
            self.details_key: (
                details if details is not None else dict(self.details_default)
            ),
        }


@dataclass(frozen=True)
class CompleteExtractorDomainConfig:
    """Konfiguracja domeny dla CompleteExtractorBase.

    Jak dodać nową domenę bez kopiowania klasy:
    1) ustaw `list_scraper_cls` lub `list_scraper_clses` oraz `single_scraper_cls`,
    2) ustaw `detail_url_field_path` lub `detail_url_field_paths`
       (np. ``"driver.url"``),
    3) opcjonalnie ustaw `record_assembly_strategy` albo `record_assembler`,
    4) opcjonalnie włącz `filter_redlinks`,
    5) opcjonalnie dodaj `record_postprocessor`, gdy wynik wymaga finalnej
       normalizacji.

    Dzięki temu nowy extractor często ogranicza się do kilku atrybutów klasowych.
    """

    list_scraper_cls: type[Any] | None = None
    list_scraper_clses: tuple[type[Any], ...] = ()
    single_scraper_cls: type[Any] | None = None
    detail_url_field_path: str | None = None
    detail_url_field_paths: tuple[str, ...] = ()
    filter_redlinks: bool = False
    record_assembly_strategy: RecordAssemblyStrategy = field(
        default_factory=AttachDetailsStrategy,
    )
    record_assembler: Callable[
        [dict[str, Any], dict[str, Any] | None],
        dict[str, Any],
    ] | None = None
    record_postprocessor: Callable[[dict[str, Any]], dict[str, Any]] | None = None

    def get_list_scraper_classes(self) -> tuple[type[Any], ...]:
        if self.list_scraper_clses:
            return self.list_scraper_clses
        if self.list_scraper_cls is not None:
            return (self.list_scraper_cls,)
        return ()

    def get_detail_url_field_paths(self) -> tuple[str, ...]:
        paths = list(self.detail_url_field_paths)
        if self.detail_url_field_path:
            paths.insert(0, self.detail_url_field_path)

        deduplicated: list[str] = []
        for path in paths:
            if path and path not in deduplicated:
                deduplicated.append(path)
        return tuple(deduplicated)
