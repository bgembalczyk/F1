from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from record_assembly_strategy.attach_details import AttachDetailsStrategy
from record_assembly_strategy.base import RecordAssemblyStrategy


@dataclass(frozen=True)
class CompleteExtractorDomainConfig:
    """Konfiguracja domeny dla CompleteExtractorBase.

    Wspierane pola konfiguracji to:
    - `list_scraper_classes`
    - `detail_url_field_paths`
    """

    list_scraper_classes: tuple[type[Any], ...] = ()
    single_scraper_cls: type[Any] | None = None
    detail_url_field_paths: tuple[str, ...] = ()

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
        object.__setattr__(
            self,
            "list_scraper_classes",
            self._dedupe(list(self.list_scraper_classes)),
        )
        object.__setattr__(
            self,
            "detail_url_field_paths",
            self._dedupe([path for path in self.detail_url_field_paths if path]),
        )

    @staticmethod
    def _dedupe(values: list[Any]) -> tuple[Any, ...]:
        deduplicated: list[Any] = []
        for value in values:
            if value not in deduplicated:
                deduplicated.append(value)
        return tuple(deduplicated)
