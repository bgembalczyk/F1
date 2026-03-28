from abc import ABC
from abc import abstractmethod
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from infrastructure.http_client.policies.http import HttpPolicy
from scrapers.base.export.exporters import DataExporter
from scrapers.base.factory.runtime_factory import ScraperRuntimeFactory
from scrapers.base.helpers.http import resolve_http_policy
from scrapers.base.logging import get_logger
from scrapers.base.options import ScraperOptions
from scrapers.base.results import ScrapeResult
from scrapers.wiki.component_metadata import validate_metadata_for_component_class


class BaseDataExtractor(ABC):
    """
    Bazowa klasa dla ekstraktorów danych, które orkiestrują wiele scraperów.

    W odróżnieniu od ABCScraper nie pobiera ani nie parsuje HTML samodzielnie -
    deleguje to do podległych scraperów.

    Kontrakt:
    - fetch() zawsze zwraca listę rekordów (może być pusta).
    """

    #: URL źródła danych (ustawiany w klasach potomnych)
    url: str

    def __init__(self, *, options: ScraperOptions) -> None:
        validate_metadata_for_component_class(type(self))
        self.logger = get_logger(self.__class__.__name__)
        self._data: list[Any] | None = None
        self.exporter = options.exporter or DataExporter()

        self.http_policy = self.get_http_policy(options)
        runtime = ScraperRuntimeFactory().build(
            options=options,
            policy=self.http_policy,
        )
        self.source_adapter = runtime.source_adapter
        self.debug_dir = Path(options.debug_dir) if options.debug_dir else None

    def get_http_policy(self, options: ScraperOptions) -> HttpPolicy:
        return resolve_http_policy(options)

    @abstractmethod
    def fetch(self) -> list[Any]:
        """Pobierz i zwróć listę rekordów."""

    def build_result(self, data: list[Any] | None = None) -> ScrapeResult:
        """Utwórz ScrapeResult z metadanymi."""
        return ScrapeResult(
            data=data if data is not None else (self._data or []),
            source_url=getattr(self, "url", None),
        )

    def to_json(
        self,
        path: str | Path,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        result = self.build_result()
        result.to_json(
            path,
            exporter=self.exporter,
            indent=indent,
            include_metadata=include_metadata,
        )

    def to_csv(
        self,
        path: str | Path,
        *,
        fieldnames: Sequence[str] | None = None,
        fieldnames_strategy: str = "union",
        include_metadata: bool = False,
    ) -> None:
        result = self.build_result()
        result.to_csv(
            path,
            exporter=self.exporter,
            fieldnames=fieldnames,
            fieldnames_strategy=fieldnames_strategy,
            include_metadata=include_metadata,
        )

    def to_dataframe(self):
        result = self.build_result()
        return result.to_dataframe()
