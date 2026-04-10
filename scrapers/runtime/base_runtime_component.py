from __future__ import annotations

from abc import ABC
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from infrastructure.http_client.policies.http import HttpPolicy
from scrapers.base.exporters.data import DataExporter
from scrapers.base.factory.source_adapter_fetcher_shim import ScraperRuntimeFactory
from scrapers.base.logging import get_logger
from scrapers.base.options import ScraperOptions
from scrapers.base.results import ScrapeResult
from scrapers.base.services.result_export_service import ResultExportService
from scrapers.base.services.result_tabular_adapter import ResultTabularAdapter
from scrapers.wiki.component_metadata_wiki import validate_metadata_for_component_class


class BaseRuntimeComponent(ABC):
    """Wspólny runtime dla scraperów i ekstraktorów.

    Kontrakt atrybutów runtime:
    - ``logger``: logger komponentu,
    - ``options``: użyte ``ScraperOptions``,
    - ``_run_id``: identyfikator przebiegu,
    - ``source_adapter`` i ``http_policy``: współdzielona bramka I/O.
    """

    url: str

    def __init__(self, *, options: ScraperOptions) -> None:
        validate_metadata_for_component_class(type(self))
        self.options = options
        self.logger = get_logger(self.__class__.__name__)
        self._run_id: str | None = options.run_id
        self._data: list[Any] | None = None

        self.include_urls = options.include_urls
        self.normalize_empty_values = options.normalize_empty_values
        self.exporter = options.exporter or DataExporter()
        self.result_export_service = ResultExportService()
        self.result_tabular_adapter = ResultTabularAdapter()
        self.debug_dir = Path(options.debug_dir) if options.debug_dir else None

        self.http_policy = self.get_http_policy(options)
        runtime = ScraperRuntimeFactory().build(options=options, policy=self.http_policy)
        self.source_adapter = runtime.source_adapter

    def get_http_policy(self, options: ScraperOptions) -> HttpPolicy:
        return options.resolve_http_policy()

    def build_result(self, data: list[Any] | None = None) -> ScrapeResult:
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
        self.result_export_service.to_json(
            result,
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
        self.result_export_service.to_csv(
            result,
            path,
            exporter=self.exporter,
            fieldnames=fieldnames,
            fieldnames_strategy=fieldnames_strategy,
            include_metadata=include_metadata,
        )

    def to_dataframe(self):
        result = self.build_result()
        return self.result_tabular_adapter.to_dataframe(result)
