from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from record_assembly_strategy.attach_details import AttachDetailsStrategy
from record_assembly_strategy.base import RecordAssemblyStrategy


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
