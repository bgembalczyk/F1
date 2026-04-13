from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Protocol
from typing import runtime_checkable

from complete_extractor.domain_config import CompleteExtractorDomainConfig
from exporters.data import DataExporter
from infrastructure.helpers import init_scraper_options
from infrastructure.http.errors.base import RequestError
from infrastructure.http.policies.http import HttpPolicy
from scrapers.adapters.result_tabular import ResultTabularAdapter
from scrapers.component_metadata_wiki import validate_metadata_for_component_class
from scrapers.errors.domain_parse import DomainParseError
from scrapers.errors.network import ScraperNetworkError
from scrapers.errors.parse import ScraperParseError
from scrapers.helpers.wiki import is_wikipedia_redlink
from scrapers.logging import get_logger
from scrapers.options import ScraperOptions
from scrapers.progress import ProgressAdapter
from scrapers.progress import TqdmProgressAdapter
from scrapers.results import ScrapeResult
from scrapers.services.result_export import ResultExportService
from scrapers.source_adapter import IterableSourceAdapter
from scrapers.source_adapter import MultiIterableSourceAdapter
from scrapers.wiring import ScraperRuntimeFactory


@runtime_checkable
class ListScraperProtocol(Protocol):
    def fetch(self) -> list[dict[str, Any]]: ...


@runtime_checkable
class SingleScraperProtocol(Protocol):
    def extract_by_url(self, url: str) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class CompositeDataExtractorChildren:
    list_scraper: ListScraperProtocol | list[ListScraperProtocol]
    single_scraper: SingleScraperProtocol
    records_adapter: (
        IterableSourceAdapter[dict[str, Any]]
        | MultiIterableSourceAdapter[dict[str, Any]]
    )


class CompleteExtractorBase(ABC):
    """Wspólny flow dla ekstraktorów typu "lista + szczegóły"."""

    DOMAIN_CONFIG = CompleteExtractorDomainConfig()

    url: str

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        progress: ProgressAdapter | None = None,
    ) -> None:
        resolved_options = init_scraper_options(options, include_urls=True)
        validate_metadata_for_component_class(type(self))
        self.logger = get_logger(self.__class__.__name__)
        self._data: list[Any] | None = None
        self.exporter = resolved_options.exporter or DataExporter()
        self.result_export_service = ResultExportService()
        self.result_tabular_adapter = ResultTabularAdapter()

        self.http_policy = self.get_http_policy(resolved_options)
        runtime = ScraperRuntimeFactory().build(
            options=resolved_options,
            policy=self.http_policy,
        )
        self.source_adapter = runtime.source_adapter
        self.debug_dir = Path(resolved_options.debug_dir) if resolved_options.debug_dir else None

        self.options = resolved_options
        self.progress = progress or TqdmProgressAdapter()
        children = self.build_children()
        self.list_scraper = children.list_scraper
        self.single_scraper = children.single_scraper
        self.records_adapter = children.records_adapter

    def get_http_policy(self, options: ScraperOptions) -> HttpPolicy:
        return options.resolve_http_policy()

    def build_children(self) -> CompositeDataExtractorChildren:
        list_scrapers = self.build_list_scrapers(self.options)
        list_scraper, records_adapter = self._build_list_sources(list_scrapers)

        return CompositeDataExtractorChildren(
            list_scraper=list_scraper,
            single_scraper=self.build_single_scraper(self.options),
            records_adapter=records_adapter,
        )

    def _build_list_sources(
        self,
        list_scrapers: list[ListScraperProtocol] | None,
    ) -> tuple[
        ListScraperProtocol | list[ListScraperProtocol],
        IterableSourceAdapter[dict[str, Any]]
        | MultiIterableSourceAdapter[dict[str, Any]],
    ]:
        if list_scrapers is None:
            list_scraper = self.build_list_scraper(self.options)
            records_adapter = IterableSourceAdapter(self._records_fetcher(list_scraper))
            return list_scraper, records_adapter
        records_adapter = MultiIterableSourceAdapter(
            [self._records_fetcher(scraper) for scraper in list_scrapers],
        )
        return list_scrapers, records_adapter

    def list_scraper_options(self, options: ScraperOptions) -> ScraperOptions:
        scraper_options = ScraperOptions(
            include_urls=True,
            source_adapter=self.source_adapter,
            debug_dir=options.debug_dir,
        )
        scraper_options.http.policy = self.http_policy
        return scraper_options

    def single_scraper_options(self, options: ScraperOptions) -> ScraperOptions:
        scraper_options = ScraperOptions(
            source_adapter=self.source_adapter,
            debug_dir=options.debug_dir,
        )
        scraper_options.http.policy = self.http_policy
        return scraper_options

    def build_list_scraper(self, options: ScraperOptions) -> ListScraperProtocol:
        """Zbuduj scraper listy dla przypadków jedno-listowych."""
        scraper_classes = self.DOMAIN_CONFIG.list_scraper_classes
        if len(scraper_classes) > 1:
            msg = (
                f"{self.__class__.__name__} definiuje wiele list scraperów; "
                "użyj build_list_scrapers()."
            )
            raise NotImplementedError(msg)

        scraper_cls = scraper_classes[0] if scraper_classes else None
        if scraper_cls is None:
            msg = (
                f"{self.__class__.__name__} musi ustawić "
                "DOMAIN_CONFIG.list_scraper_classes "
                "lub nadpisać build_list_scraper()."
            )
            raise NotImplementedError(msg)
        return scraper_cls(options=self.list_scraper_options(options))

    def build_list_scrapers(
        self,
        options: ScraperOptions,
    ) -> list[ListScraperProtocol] | None:
        """Opcjonalny hook dla przypadków wielolistowych."""
        scraper_classes = self.DOMAIN_CONFIG.list_scraper_classes
        if len(scraper_classes) <= 1:
            return None
        return [
            scraper_cls(options=self.list_scraper_options(options))
            for scraper_cls in scraper_classes
        ]

    def build_single_scraper(self, options: ScraperOptions) -> SingleScraperProtocol:
        """Zbuduj scraper szczegółów."""
        scraper_cls = self.DOMAIN_CONFIG.single_scraper_cls
        if scraper_cls is None:
            msg = (
                f"{self.__class__.__name__} musi ustawić "
                "DOMAIN_CONFIG.single_scraper_cls "
                "lub nadpisać build_single_scraper()."
            )
            raise NotImplementedError(msg)
        return scraper_cls(options=self.single_scraper_options(options))

    def get_detail_url(self, _record: dict[str, Any]) -> str | None:
        return None

    def extract_detail_url(self, record: dict[str, Any]) -> str | None:
        """Wyciągnij URL szczegółów z rekordu listy na podstawie field path."""
        for field_path in self.DOMAIN_CONFIG.detail_url_field_paths:
            value = self._get_value_by_path(record, field_path)
            if not isinstance(value, str) or not value:
                continue
            if self.DOMAIN_CONFIG.filter_redlinks and is_wikipedia_redlink(value):
                continue
            return value
        return None

    def assemble_record(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        assembler = self.DOMAIN_CONFIG.record_assembler
        if assembler is not None:
            assembled = assembler(record, details)
        else:
            assembled = self.DOMAIN_CONFIG.record_assembly_strategy.assemble(
                record,
                details,
            )

        postprocessor = self.DOMAIN_CONFIG.record_postprocessor
        if postprocessor is not None:
            return postprocessor(assembled)

        return assembled

    def fetch(self) -> list[dict[str, Any]]:
        records = self.records_adapter.get()
        complete: list[dict[str, Any]] = []

        extractor_name = self.__class__.__name__
        wrapped_records = self._wrap_records_with_progress(
            records,
            desc=extractor_name,
            unit="item",
        )
        for record in wrapped_records:
            if not isinstance(record, dict):
                msg = (
                    "Records adapter musi zwracać dict, "
                    f"otrzymano: {type(record).__name__}"
                )
                raise TypeError(msg)

            detail_url = self.get_detail_url(record)
            details: dict[str, Any] | None = None

            if detail_url:
                try:
                    details_list = self.single_scraper.extract_by_url(detail_url)
                    details = details_list[0] if details_list else None
                except (
                    RequestError,
                    ScraperNetworkError,
                    ScraperParseError,
                    DomainParseError,
                ):
                    self.logger.exception(
                        "Nie udało się pobrać szczegółów rekordu (url=%s).",
                        detail_url,
                    )

            complete.append(self.assemble_record(record, details))

        self._data = complete
        return self._data

    def _wrap_records_with_progress(self, records, *, desc: str, unit: str):
        wrap = self.progress.wrap
        try:
            return wrap(records, desc=desc, unit=unit)
        except TypeError:
            pass
        try:
            return wrap(records, _desc=desc, _unit=unit)
        except TypeError:
            pass
        try:
            return wrap(records, desc, unit)
        except TypeError:
            return wrap(records)

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

    @staticmethod
    def _get_value_by_path(source: dict[str, Any], field_path: str) -> Any:
        current: Any = source
        for part in field_path.split("."):
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current

    def _records_fetcher(self, scraper: ListScraperProtocol):
        def _fetch() -> list[dict[str, Any]]:
            try:
                return scraper.fetch()
            except (
                RequestError,
                ScraperNetworkError,
                ScraperParseError,
                DomainParseError,
            ):
                self.logger.exception(
                    "Nie udało się pobrać listy rekordów (%s).",
                    scraper.__class__.__name__,
                )
                return []

        return _fetch
