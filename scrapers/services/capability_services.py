from __future__ import annotations

from collections.abc import Callable
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from scrapers.adapters.result_tabular import ResultTabularAdapter
from scrapers.results import ScrapeResult
from scrapers.services.result_export import ResultExportService
from scrapers.validation_runner import ValidationRunner

if TYPE_CHECKING:
    from logging import Logger

    from validation.validator_base import ExportRecord
    from validation.validator_base import RecordValidator


class ValidationCapabilityService:
    """Validation capability delegated from template-method base scrapers."""

    def __init__(
        self,
        *,
        validation_mode: str,
        validator: RecordValidator | None,
        logger: Logger,
        url_provider: Callable[[], str | None],
        write_quality_report: Callable[[], None],
        validation_runner_factory: Callable[..., ValidationRunner],
    ) -> None:
        self.validation_mode = validation_mode
        self.validator = validator
        self._logger = logger
        self._url_provider = url_provider
        self._write_quality_report = write_quality_report
        self._validation_runner_factory = validation_runner_factory

    def assert_mode_supported(self) -> None:
        if self.validation_mode in {"soft", "hard"}:
            return
        msg = "validation_mode must be 'soft' (drop record + warn) or 'hard' (raise)"
        raise ValueError(msg)

    def validate_records(self, records: list[ExportRecord]) -> list[ExportRecord]:
        if self.validator is None:
            return records
        return self._build_runner().validate(records)

    def _build_runner(self) -> ValidationRunner:
        return self._validation_runner_factory(
            validator=self.validator,
            validation_mode=self.validation_mode,
            logger=self._logger,
            write_quality_report=self._write_quality_report,
            url=self._url_provider(),
        )


class ExportCapabilityService:
    """Export capability delegated from base scrapers via composition."""

    def __init__(
        self,
        *,
        result_export_service: ResultExportService,
        result_tabular_adapter: ResultTabularAdapter,
        fetch_data: Callable[[], list[ExportRecord]],
        source_url_provider: Callable[[], str | None],
        exporter_provider: Callable[[], object],
    ) -> None:
        self._result_export_service = result_export_service
        self._result_tabular_adapter = result_tabular_adapter
        self._fetch_data = fetch_data
        self._source_url_provider = source_url_provider
        self._exporter_provider = exporter_provider

    def build_result(self, data: list[ExportRecord] | None = None) -> ScrapeResult:
        return ScrapeResult(
            data=data if data is not None else self._fetch_data(),
            source_url=self._source_url_provider(),
        )

    def to_json(
        self,
        path: str | Path,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        result = self.build_result()
        self._result_export_service.to_json(
            result,
            path,
            exporter=self._exporter_provider(),
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
        self._result_export_service.to_csv(
            result,
            path,
            exporter=self._exporter_provider(),
            fieldnames=fieldnames,
            fieldnames_strategy=fieldnames_strategy,
            include_metadata=include_metadata,
        )

    def to_dataframe(self):
        result = self.build_result()
        return self._result_tabular_adapter.to_dataframe(result)


class ReportingCapabilityService:
    """Quality reporting delegation service for scraper lifecycle events."""

    def __init__(
        self,
        *,
        quality_report_service,
        logger: Logger,
        run_id_provider: Callable[[], str | None],
    ) -> None:
        self._quality_report_service = quality_report_service
        self._logger = logger
        self._run_id_provider = run_id_provider

    def set_run_context(self, run_id: str) -> None:
        self._quality_report_service.set_run_id(run_id)

    def write_step_quality_report(
        self,
        *,
        step_name: str,
        records: list[dict[str, object]],
    ) -> None:
        self._quality_report_service.write_step(step_name=step_name, records=records)

    def write_quality_report(self) -> None:
        self._quality_report_service.write_validation_report()

    def log_start(self, url: str) -> None:
        self._logger.debug(
            "Scrape run %s started for url=%s",
            self._run_id_provider(),
            url,
        )
