import warnings
from abc import ABC
from collections.abc import Sequence
from pathlib import Path
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol
from typing import TypeVar
from uuid import uuid4

from bs4 import BeautifulSoup

from infrastructure.http_client.policies.http import HttpPolicy
from scrapers.base.errors import ScraperError
from scrapers.base.errors import ScraperNetworkError
from scrapers.base.errors import ScraperParseError
from scrapers.base.helpers.url import normalize_url
from scrapers.base.logging import get_logger
from scrapers.base.options import ScraperOptions
from scrapers.base.post_processors import apply_post_processors
from scrapers.base.records import NormalizedRecord
from scrapers.base.records import RawRecord
from scrapers.base.results import ScrapeResult
from scrapers.base.scraper_components import ErrorPolicy
from scrapers.base.scraper_components import PipelineOrchestrator
from scrapers.base.scraper_components import QualityReportService
from scrapers.base.scraper_components import RuntimeInitializer
from scrapers.base.services.result_export_service import ResultExportService
from scrapers.base.services.result_tabular_adapter import ResultTabularAdapter
from scrapers.base.transformers.helpers import apply_transformers
from scrapers.base.validation_runner import ValidationRunner
from scrapers.mixins.run_diagnostics import RunDiagnosticsMixin
from scrapers.wiki.component_metadata_wiki import validate_metadata_for_component_class
from validation.validator_base import ExportRecord

T = TypeVar("T")


class ScraperLifecycleProtocol(Protocol):
    def fetch(self) -> list[ExportRecord]: ...

    def parse(self, soup: BeautifulSoup) -> list[RawRecord]: ...

    def build_result(self, data: list[ExportRecord] | None = None) -> ScrapeResult: ...


class ScraperLifecycleABC(ABC):
    @abstractmethod
    def fetch(self) -> list[ExportRecord]:
        """Execute fetch lifecycle and return exportable records."""

    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> list[RawRecord]:
        """Parse BeautifulSoup document into raw records."""

    @abstractmethod
    def build_result(self, data: list[ExportRecord] | None = None) -> ScrapeResult:
        """Build finalized scrape result with metadata."""


class BaseScraperCore(ScraperLifecycleABC, ABC):
    """Minimal core with lifecycle contract and minimal state."""

    url: str

    def __init__(self, *, options: ScraperOptions) -> None:
        validate_metadata_for_component_class(type(self))
        self.include_urls = options.include_urls
        self.normalize_empty_values = options.normalize_empty_values
        self.logger = get_logger(self.__class__.__name__)
        self._run_id: str | None = options.run_id
        self.debug_dir = Path(options.debug_dir) if options.debug_dir else None
        self._validation_mode = "soft"
        self._data: list[ExportRecord] | None = None

    @property
    def validation_mode(self) -> str:
        return self._validation_mode

    @validation_mode.setter
    def validation_mode(self, value: str) -> None:
        self._validation_mode = value


class FetchOrchestrationMixin:
    """Fetch orchestration and runtime wiring mixin."""

    def _initialize_runtime(self, options: ScraperOptions) -> None:
        runtime = RuntimeInitializer(
            resolve_http_policy=self.get_http_policy,
        ).initialize(
            options=options,
            logger=self.logger,
            normalize_empty_values=self.normalize_empty_values,
            default_validator=getattr(self, "default_validator", None),
        )
        self.http_policy = runtime.http_policy
        self.source_adapter = runtime.source_adapter
        self.fetcher = runtime.fetcher
        self.parser = runtime.parser
        self.exporter = runtime.exporter
        self._record_normalizer = runtime.record_normalizer
        self.transformers = runtime.transformers
        self.post_processors = runtime.post_processors
        self.validator = runtime.validator
        self._validation_mode = runtime.validation_mode
        self._error_policy = self._create_error_policy(runtime=runtime, options=options)

    def _create_error_policy(
        self,
        *,
        runtime,
        options: ScraperOptions,
    ) -> ErrorPolicy:
        return ErrorPolicy(
            error_handler=runtime.error_handler,
            logger=self.logger,
            get_url=lambda: getattr(self, "url", None),
            policy=options.error_policy,
            retry_attempts=options.error_retry_attempts,
        )

    def _initialize_pipeline_orchestrator(self) -> None:
        self._pipeline_orchestrator = self._create_pipeline_orchestrator()

    def _create_pipeline_orchestrator(self) -> PipelineOrchestrator:
        return PipelineOrchestrator(
            logger=self.logger,
            quality_report_service=self._quality_report_service,
            error_policy=self._error_policy,
            parse_records=self.parse,
            normalize_records=self._normalize_pipeline_records,
            transform_records=self._apply_transformers,
            validate_records=self.validate_records,
            post_process_records=self.post_process_records,
        )

    def fetch(self) -> list[ExportRecord]:
        self._validate_fetch_url()
        run_id = self._start_run()
        data = self._pipeline_orchestrator.run_fetch(
            run_id=run_id,
            download_html=self._download,
        )
        if data is None:
            self._data = []
            return self._data

        self._data = data
        self.logger.debug("Scrape run %s finished", run_id)
        return self._data

    def _validate_fetch_url(self) -> None:
        if getattr(self, "url", None):
            return
        msg = "Scraper.url musi być ustawiony przed fetch()."
        raise ValueError(msg)

    def _start_run(self) -> str:
        run_id = self._run_id or uuid4().hex
        self._run_id = run_id
        self._error_policy.set_run_id(run_id)
        self._quality_report_service.set_run_id(run_id)
        self.logger.debug("Scrape run %s started for url=%s", run_id, self.url)
        return run_id

    def _normalize_pipeline_records(
        self,
        records: list[RawRecord],
    ) -> list[NormalizedRecord]:
        return self._record_normalizer.normalize(records)


class ValidationMixin:
    def _validate_validation_mode(self) -> None:
        if self._validation_mode in {"soft", "hard"}:
            return
        msg = "validation_mode must be 'soft' (drop record + warn) or 'hard' (raise)"
        raise ValueError(msg)

    def validate_records(self, records: list[ExportRecord]) -> list[ExportRecord]:
        if self.validator is None:
            return records
        return self._build_validation_runner().validate(records)

    def _build_validation_runner(self) -> ValidationRunner:
        return PipelineOrchestrator.build_validation_runner(
            validator=self.validator,
            validation_mode=self.validation_mode,
            logger=self.logger,
            write_quality_report=self._write_quality_report,
            url=getattr(self, "url", None),
        )


class ExportMixin:
    def _initialize_export_services(self) -> None:
        self.result_export_service = self._create_result_export_service()
        self.result_tabular_adapter = self._create_result_tabular_adapter()

    def _create_result_export_service(self) -> ResultExportService:
        return ResultExportService()

    def _create_result_tabular_adapter(self) -> ResultTabularAdapter:
        return ResultTabularAdapter()

    def get_data(self) -> list[ExportRecord]:
        if self._data is None:
            return self.fetch()
        return self._data

    def build_result(self, data: list[ExportRecord] | None = None) -> ScrapeResult:
        return ScrapeResult(
            data=data if data is not None else self.get_data(),
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


class QualityReportMixin:
    def _initialize_quality_report_service(self) -> None:
        self._quality_report_service = self._create_quality_report_service()

    def _create_quality_report_service(self) -> QualityReportService:
        return QualityReportService(
            enabled=self._quality_report_enabled,
            debug_dir=self.debug_dir,
            run_id=self._run_id,
            source_metadata_provider=self._source_metadata,
            logger=self.logger,
            validator_provider=lambda: self.validator,
            debug_diff_domains=self._debug_diff_domains,
            debug_diff_record_ids=self._debug_diff_record_ids,
        )

    def _write_step_quality_report(
        self,
        *,
        step_name: str,
        records: list[dict[str, object]],
    ) -> None:
        self._quality_report_service.write_step(step_name=step_name, records=records)

    def _write_quality_report(self) -> None:
        self._quality_report_service.write_validation_report()


class ABCScraper(
    ExportMixin,
    ValidationMixin,
    QualityReportMixin,
    FetchOrchestrationMixin,
    BaseScraperCore,
):
    """
    Bazowa klasa dla wszystkich scraperów F1.

    Odpowiada za:
    - orkiestrację download → parse → normalize → export-records
    - trzymanie danych w pamięci
    - delegowanie eksportu
    - wspólną obsługę błędów (network/parse + soft-skip)

    Kontrakt:
    - fetch() zawsze zwraca listę ExportRecord (może być pusta).
    """

    def __init__(self, *, options: ScraperOptions) -> None:
        super().__init__(options=options)
        self._quality_report_enabled = options.quality_report
        self._debug_diff_domains = options.debug_diff_domains
        self._debug_diff_record_ids = options.debug_diff_record_ids
        self._initialize_runtime(options)
        self._validate_validation_mode()
        self._initialize_quality_report_service()
        self._initialize_pipeline_orchestrator()
        self._initialize_export_services()

    # ---------- API wysokiego poziomu ----------

    def _finalize_fetch(
        self,
        run_id: str,
        data: list[ExportRecord],
    ) -> list[ExportRecord]:
        """Backward-compatible alias for legacy subclasses overriding finalization."""
        warnings.warn(
            "ABCScraper._finalize_fetch() is deprecated; use "
            "fetch() return path instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._data = data
        self.logger.debug("Scrape run %s finished", run_id)
        return self._data

    def _download(self) -> str:
        # Adapter jest jedyną “bramką” do źródła (może być CacheAdapter).
        return self.fetch_html(self.url)

    def fetch_html(self, url: str) -> str:
        return self.source_adapter.get(url)

    def _parse_soup(self, _soup: BeautifulSoup) -> list[RawRecord]:
        """Parsowanie BS4 -> lista rekordów surowych."""
        warnings.warn(
            "ABCScraper._parse_soup() is deprecated; implement parse_records() "
            "instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.parse_records(_soup)

    def parse_records(self, _soup: BeautifulSoup) -> list[RawRecord]:
        """Primary extension point for parsing BeautifulSoup into raw records."""
        msg = (
            f"{self.__class__.__name__} must implement parse_records() "
            "or override parse()."
        )
        raise NotImplementedError(
            msg,
        )

    def parse(self, soup: BeautifulSoup) -> list[RawRecord]:
        if self.parser is not None:
            return self.parser.parse(soup)

        parse_impl = type(self).parse_records
        if parse_impl is not ABCScraper.parse_records:
            return self.parse_records(soup)

        legacy_parse_impl = type(self)._parse_soup  # noqa: SLF001
        if legacy_parse_impl is not ABCScraper._parse_soup:
            return self._parse_soup(soup)

        self.logger.debug(
            "No parser/parse_records implementation for %s; returning empty list.",
            self.__class__.__name__,
        )
        return []

    def parse_soup(self, soup: BeautifulSoup) -> list[RawRecord]:
        """Public facade for parsing an already constructed BeautifulSoup document."""
        return self.parse(soup)

    # ---------- Hooki: normalize/export ----------

    @staticmethod
    def to_export_records(records: list[NormalizedRecord]) -> list[ExportRecord]:
        return records

    def post_process_records(self, records: list[ExportRecord]) -> list[ExportRecord]:
        processed = apply_post_processors(
            self.post_processors,
            records,
            logger=self.logger,
        )
        self.logger.debug(
            "Post-process records: %d -> %d",
            len(records),
            len(processed),
        )
        return processed

    def _source_metadata(self) -> dict[str, object]:
        return {
            "domain": self.__module__.split(".")[1]
            if "." in self.__module__
            else self.__module__,
            "scraper": self.__class__.__name__,
            "scraper_kind": getattr(self, "scraper_kind", "single"),
            "url": getattr(self, "url", ""),
        }

    def _apply_transformers(self, records: list[ExportRecord]) -> list[ExportRecord]:
        return apply_transformers(self.transformers, records, logger=self.logger)

    # ---------- Pomocnicze ----------

    def _full_url(self, href: str) -> str | None:
        return normalize_url(self.url, href)

    def get_http_policy(self, options: ScraperOptions) -> HttpPolicy:
        return options.resolve_http_policy()

    # ---------- Error handling ----------

    def _wrap_network_error(self, exc: Exception) -> ScraperNetworkError:
        return self._error_policy.wrap_network(exc)

    def _wrap_parse_error(self, exc: Exception) -> ScraperParseError:
        return self._error_policy.wrap_parse(exc)

    def _handle_scraper_error(self, error: ScraperError) -> bool:
        return self._error_policy.handle(error)
