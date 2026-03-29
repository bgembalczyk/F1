from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from typing import Any


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

    Kanoniczne pola konfiguracji to:
    - `list_scraper_classes`
    - `detail_url_field_paths`

    Pola legacy (`list_scraper_cls`, `list_scraper_clses`, `detail_url_field_path`)
    są wspierane tymczasowo przez warstwę kompatybilności uruchamianą w
    `__post_init__`.
    """

    list_scraper_classes: tuple[type[Any], ...] = ()
    single_scraper_cls: type[Any] | None = None
    detail_url_field_paths: tuple[str, ...] = ()

    # Legacy compatibility (temporary)
    list_scraper_cls: type[Any] | None = None
    list_scraper_clses: tuple[type[Any], ...] = ()
    detail_url_field_path: str | None = None

    filter_redlinks: bool = False
    record_assembly_strategy: RecordAssemblyStrategy = field(
        default_factory=AttachDetailsStrategy,
    )
    record_assembler: (
        Callable[
            [dict[str, Any], dict[str, Any] | None],
            dict[str, Any],
        ]
        | None
    ) = None
    record_postprocessor: Callable[[dict[str, Any]], dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        self._normalize_config_fields()

    def _normalize_config_fields(self) -> None:
        normalized_list_classes = self._normalize_list_scraper_classes()
        normalized_detail_paths = self._normalize_detail_url_field_paths()
        object.__setattr__(self, "list_scraper_classes", normalized_list_classes)
        object.__setattr__(self, "detail_url_field_paths", normalized_detail_paths)

    def _normalize_list_scraper_classes(self) -> tuple[type[Any], ...]:
        classes = list(self.list_scraper_classes)

        if self.list_scraper_clses:
            classes = [*self.list_scraper_clses, *classes]
        if self.list_scraper_cls is not None:
            classes = [self.list_scraper_cls, *classes]

        return self._dedupe(classes)

    def _normalize_detail_url_field_paths(self) -> tuple[str, ...]:
        paths = list(self.detail_url_field_paths)

        if self.detail_url_field_path:
            paths = [self.detail_url_field_path, *paths]

        return self._dedupe([path for path in paths if path])

    @staticmethod
    def _dedupe(values: list[Any]) -> tuple[Any, ...]:
        deduplicated: list[Any] = []
        for value in values:
            if value not in deduplicated:
                deduplicated.append(value)
        return tuple(deduplicated)
