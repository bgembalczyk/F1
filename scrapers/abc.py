from collections.abc import Sequence
from pathlib import Path
from typing import TypeVar

from bs4 import BeautifulSoup

from infrastructure.http.policies.http import HttpPolicy
from scrapers.adapters.result_tabular import ResultTabularAdapter
from scrapers.base_core import BaseScraperCore
from scrapers.errors.base import ScraperError
from scrapers.errors.network import ScraperNetworkError
from scrapers.errors.parse import ScraperParseError
from scrapers.helpers.url import normalize_url
from scrapers.options import ScraperOptions
from scrapers.orchestration.fetch_orchestration_mixin import FetchOrchestrationMixin
from scrapers.post_processors import apply_post_processors
from scrapers.results import ScrapeResult
from scrapers.runners.pipeline_runner import NormalizedRecord
from scrapers.runners.pipeline_runner import RawRecord
from scrapers.scraper_components import PipelineOrchestrator
from scrapers.scraper_components import QualityReportService
from scrapers.services.capability_services import ExportCapabilityService
from scrapers.services.capability_services import ReportingCapabilityService
from scrapers.services.capability_services import ValidationCapabilityService
from scrapers.services.result_export import ResultExportService
from scrapers.transformers.helpers import apply_transformers
from validation.validator_base import ExportRecord

T = TypeVar("T")








class ABCScraper(
    FetchOrchestrationMixin,
    BaseScraperCore,
):
    """Template-method base scraper with composition for cross-cutting concerns."""

    def __init__(self, *, options: ScraperOptions) -> None:
        super().__init__(options=options)
        self._quality_report_enabled = options.quality_report
        self._debug_diff_domains = options.debug_diff_domains
        self._debug_diff_record_ids = options.debug_diff_record_ids
        self._initialize_runtime(options)
        self._initialize_quality_reporting()
        self._initialize_validation_capability()
        self._initialize_export_capability()
        self._validation_service.assert_mode_supported()
        self._initialize_pipeline_orchestrator()

    def _initialize_quality_reporting(self) -> None:
        self._quality_report_service = self._create_quality_report_service()
        self._reporting_service = ReportingCapabilityService(
            quality_report_service=self._quality_report_service,
            logger=self.logger,
            run_id_provider=lambda: self._run_id,
        )

    def _initialize_validation_capability(self) -> None:
        self._validation_service = ValidationCapabilityService(
            validation_mode=self.validation_mode,
            validator=self.validator,
            logger=self.logger,
            url_provider=lambda: getattr(self, "url", None),
            write_quality_report=self._write_quality_report,
            validation_runner_factory=PipelineOrchestrator.build_validation_runner,
        )

    def _initialize_export_capability(self) -> None:
        self.result_export_service = ResultExportService()
        self.result_tabular_adapter = ResultTabularAdapter()
        self._export_service = ExportCapabilityService(
            result_export_service=self.result_export_service,
            result_tabular_adapter=self.result_tabular_adapter,
            fetch_data=self.get_data,
            source_url_provider=lambda: getattr(self, "url", None),
            exporter_provider=lambda: self.exporter,
        )

    # ---------- API wysokiego poziomu ----------

    def get_data(self) -> list[ExportRecord]:
        if self._data is None:
            return self.fetch()
        return self._data

    def validate_records(self, records: list[ExportRecord]) -> list[ExportRecord]:
        self._validation_service.validation_mode = self.validation_mode
        self._validation_service.validator = self.validator
        return self._validation_service.validate_records(records)

    def build_result(self, data: list[ExportRecord] | None = None) -> ScrapeResult:
        return self._export_service.build_result(data)

    def to_json(
        self,
        path: str | Path,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        self._export_service.to_json(
            path,
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
        self._export_service.to_csv(
            path,
            fieldnames=fieldnames,
            fieldnames_strategy=fieldnames_strategy,
            include_metadata=include_metadata,
        )

    def to_dataframe(self):
        return self._export_service.to_dataframe()

    def _download(self) -> str:
        return self.fetch_html(self.url)

    def fetch_html(self, url: str) -> str:
        return self.source_adapter.get(url)

    def parse_records(self, _soup: BeautifulSoup) -> list[RawRecord]:
        msg = (
            f"{self.__class__.__name__} must implement parse_records() "
            "or override parse()."
        )
        raise NotImplementedError(msg)

    def parse(self, soup: BeautifulSoup) -> list[RawRecord]:
        if self.parser is not None:
            return self.parser.parse(soup)

        parse_impl = type(self).parse_records
        if parse_impl is not ABCScraper.parse_records:
            return self.parse_records(soup)

        self.logger.debug(
            "No parser/parse_records implementation for %s; returning empty list.",
            self.__class__.__name__,
        )
        return []

    def parse_soup(self, soup: BeautifulSoup) -> list[RawRecord]:
        return self.parse(soup)

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
        self._reporting_service.write_step_quality_report(
            step_name=step_name,
            records=records,
        )

    def _write_quality_report(self) -> None:
        self._reporting_service.write_quality_report()

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

    def _full_url(self, href: str) -> str | None:
        return normalize_url(self.url, href)

    def get_http_policy(self, options: ScraperOptions) -> HttpPolicy:
        return options.resolve_http_policy()

    def _wrap_network_error(self, exc: Exception) -> ScraperNetworkError:
        return self._error_policy.wrap_network(exc)

    def _wrap_parse_error(self, exc: Exception) -> ScraperParseError:
        return self._error_policy.wrap_parse(exc)

    def _handle_scraper_error(self, error: ScraperError) -> bool:
        return self._error_policy.handle(error)
