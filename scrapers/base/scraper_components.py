from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from typing import TypeVar

from infrastructure.http_client.requests_shim.request_error import RequestError
from models.mappers.serialization import to_dict_list
from scrapers.base.error_codes import resolve_error_code
from scrapers.base.error_handler import ErrorHandler
from scrapers.base.errors import ScraperError
from scrapers.base.errors import ScraperNetworkError
from scrapers.base.errors import ScraperParseError
from scrapers.base.export.exporters import DataExporter
from scrapers.base.factory.runtime_factory import ScraperRuntimeFactory
from scrapers.base.helpers.transformers import build_transformers
from scrapers.base.normalization import RecordNormalizer
from scrapers.base.pipeline_runner import ScraperPipelineRunner
from scrapers.base.quality.reporter import CompactStepDiffWriter
from scrapers.base.quality.reporter import QualityReporter
from scrapers.base.validation_runner import ValidationRunner
from validation.record_factory_validator import adapt_record_factory_validator

if TYPE_CHECKING:
    from collections.abc import Callable

    from infrastructure.http_client.policies.http import HttpPolicy
    from scrapers.base.options import ScraperOptions
    from scrapers.base.records import NormalizedRecord
    from scrapers.base.records import RawRecord
    from validation.validator_base import ExportRecord
    from validation.validator_base import RecordValidator

T = TypeVar("T")


@dataclass(slots=True)
class RuntimeComponents:
    http_policy: HttpPolicy
    source_adapter: object
    fetcher: object
    parser: object | None
    exporter: DataExporter
    record_normalizer: RecordNormalizer
    transformers: list[object]
    post_processors: list[object]
    error_handler: ErrorHandler
    validator: RecordValidator | None
    validation_mode: str


class RuntimeInitializer:
    """Buduje runtime scrapera i zwraca jawny kontrakt komponentów."""

    def __init__(
        self,
        *,
        resolve_http_policy: Callable[[ScraperOptions], HttpPolicy],
    ) -> None:
        self._resolve_http_policy = resolve_http_policy

    def initialize(
        self,
        *,
        options: ScraperOptions,
        logger,
        normalize_empty_values: bool,
        default_validator: RecordValidator | None,
    ) -> RuntimeComponents:
        http_policy = self._resolve_http_policy(options)
        runtime = ScraperRuntimeFactory().build(options=options, policy=http_policy)
        validator = options.validator or default_validator
        if validator is not None:
            validator.set_record_factory_validator(
                adapt_record_factory_validator(options.record_factory),
            )
        return RuntimeComponents(
            http_policy=http_policy,
            source_adapter=runtime.source_adapter,
            fetcher=runtime.fetcher,
            parser=options.parser,
            exporter=options.exporter or DataExporter(),
            record_normalizer=RecordNormalizer(
                normalize_empty_values=normalize_empty_values,
            ),
            transformers=build_transformers(options.pipeline.transformers),
            post_processors=list(options.pipeline.post_processors or []),
            error_handler=ErrorHandler(
                logger=logger,
                debug_dir=options.debug_dir,
                error_report_enabled=options.error_report,
                run_id=options.run_id,
            ),
            validator=validator,
            validation_mode=options.validation_mode,
        )


class ErrorPolicy:
    """Obsługuje mapowanie i decyzję soft/hard dla błędów scrapera."""

    def __init__(
        self,
        *,
        error_handler: ErrorHandler,
        logger,
        get_url: Callable[[], str | None],
        policy: str = "fail-fast",
        retry_attempts: int = 1,
    ) -> None:
        self._error_handler = error_handler
        self._logger = logger
        self._get_url = get_url
        self._policy = policy
        self._retry_attempts = retry_attempts

    def set_run_id(self, run_id: str | None) -> None:
        self._error_handler.set_run_id(run_id)

    def wrap_network(self, exc: Exception) -> ScraperNetworkError:
        return self._error_handler.wrap_network(exc, url=self._get_url())

    def wrap_parse(self, exc: Exception) -> ScraperParseError:
        return self._error_handler.wrap_parse(exc, url=self._get_url())

    def handle(self, error: ScraperError) -> bool:
        return self._error_handler.handle(error)

    def handle_exception(self, exc: Exception, error: ScraperError):
        self._logger.debug(
            "Scraper error for url=%s (type=%s): %s",
            self._get_url(),
            type(error).__name__,
            error,
        )
        if self.handle(error):
            return
        if error is exc:
            raise exc
        raise error from exc

    @property
    def policy(self) -> str:
        return self._policy

    @property
    def retry_attempts(self) -> int:
        return self._retry_attempts

    def should_retry(self, *, attempt: int) -> bool:
        return self._policy == "retry" and attempt < self._retry_attempts

    def should_skip(self) -> bool:
        return self._policy == "skip"

    def handle_recoverable_exception(
        self,
        *,
        exc: Exception,
        error: ScraperError,
        attempt: int,
    ):
        if self.should_retry(attempt=attempt):
            code_definition = resolve_error_code(error.code)
            self._logger.warning(
                "Recoverable warning [%s|%s] for url=%s (attempt %d/%d): %s",
                code_definition.code_id,
                code_definition.short_description,
                self._get_url(),
                attempt + 1,
                self._retry_attempts,
                exc,
            )
            return "retry"
        if self.should_skip():
            code_definition = resolve_error_code(error.code)
            self._logger.warning(
                "Recoverable warning [%s|%s] for url=%s. Skip by policy '%s': %s",
                code_definition.code_id,
                code_definition.short_description,
                self._get_url(),
                self._policy,
                exc,
            )
            return None
        return self.handle_exception(exc, error)


class QualityReportService:
    def __init__(
        self,
        *,
        enabled: bool,
        debug_dir: Path | None,
        run_id: str | None,
        source_metadata_provider: Callable[[], dict[str, object]],
        logger,
        validator_provider: Callable[[], RecordValidator | None],
        debug_diff_domains: set[str] | None = None,
        debug_diff_record_ids: set[str] | None = None,
    ) -> None:
        self._enabled = enabled
        self._debug_dir = debug_dir
        self._run_id = run_id
        self._source_metadata_provider = source_metadata_provider
        self._logger = logger
        self._validator_provider = validator_provider
        self._reporter: QualityReporter | None = None
        self._diff_writer: CompactStepDiffWriter | None = None

        if self._enabled:
            self._reporter = QualityReporter(
                report_root=self._resolve_report_root(),
                run_id=run_id or "pending",
                source_metadata=self._source_metadata_provider(),
            )
            if self._debug_dir is not None:
                self._diff_writer = CompactStepDiffWriter(
                    debug_dir=self._debug_dir,
                    run_id=run_id or "pending",
                    domain_filter=debug_diff_domains,
                    record_id_filter=debug_diff_record_ids,
                )

    def set_run_id(self, run_id: str) -> None:
        self._run_id = run_id
        if self._diff_writer is not None:
            self._diff_writer.set_run_id(run_id)

    def write_step(self, *, step_name: str, records: list[dict[str, object]]) -> None:
        if not self._enabled or self._reporter is None:
            return
        run_id = self._run_id or "no_run_id"
        self._reporter.run_id = run_id
        step_id = f"{run_id}_{step_name}"
        report_path = self._reporter.report_step(
            step_id=step_id,
            records=records,
            source_metadata=self._source_metadata_provider(),
        )
        self._logger.debug("Saved step quality report: %s", report_path)
        if self._diff_writer is not None:
            diff_path = self._diff_writer.write_step_diff(
                step_name=step_name,
                records=records,
                source_metadata=self._source_metadata_provider(),
            )
            if diff_path is not None:
                self._logger.debug("Saved compact step diffs: %s", diff_path)

    def write_validation_report(self) -> None:
        validator = self._validator_provider()
        if not self._enabled or self._debug_dir is None or validator is None:
            return
        report_path = validator.write_quality_report(self._debug_dir)
        self._logger.info("Saved quality report: %s", report_path)

    def write_error_summary(self, payload: dict[str, object]) -> None:
        if not self._enabled:
            return
        run_id = str(payload.get("run_id") or self._run_id or "no_run_id")
        report_root = self._resolve_report_root()
        report_root.mkdir(parents=True, exist_ok=True)
        report_path = report_root / f"error_summary_{run_id}.json"
        report_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self._logger.debug("Saved error summary report: %s", report_path)

    def _resolve_report_root(self) -> Path:
        if self._debug_dir is not None:
            return self._debug_dir
        return Path("data/checkpoints")


class PipelineOrchestrator:
    def __init__(
        self,
        *,
        logger,
        quality_report_service: QualityReportService,
        error_policy: ErrorPolicy,
        parse_records: Callable,
        normalize_records: Callable[[list[RawRecord]], list[NormalizedRecord]],
        transform_records: Callable[[list[NormalizedRecord]], list[ExportRecord]],
        validate_records: Callable[[list[ExportRecord]], list[ExportRecord]],
        post_process_records: Callable[[list[ExportRecord]], list[ExportRecord]],
    ) -> None:
        self._logger = logger
        self._quality_report_service = quality_report_service
        self._error_policy = error_policy
        self._pipeline_runner = ScraperPipelineRunner(
            logger=logger,
            write_step_quality_report=self._write_pipeline_quality_report,
            write_error_summary_report=self._write_pipeline_error_summary,
            parse_records=parse_records,
            normalize_records=normalize_records,
            transform_records=transform_records,
            validate_records=validate_records,
            post_process_records=post_process_records,
        )

    def run_fetch(
        self,
        *,
        run_id: str,
        download_html: Callable[[], str],
    ) -> list[ExportRecord] | None:
        html = self._download_with_error_handling(
            run_id=run_id,
            download_html=download_html,
        )
        if html is None:
            return None
        return self._parse_pipeline_with_error_handling(run_id=run_id, html=html)

    def _download_with_error_handling(
        self,
        *,
        run_id: str,
        download_html: Callable[[], str],
    ) -> str | None:
        attempt = 0
        while True:
            should_retry, result = self._download_once(
                run_id=run_id,
                download_html=download_html,
                attempt=attempt,
            )
            if should_retry:
                attempt += 1
                continue
            return result

    def _download_once(
        self,
        *,
        run_id: str,
        download_html: Callable[[], str],
        attempt: int,
    ) -> tuple[bool, str | None]:
        try:
            self._logger.debug("Scrape run %s: start download", run_id)
            html = download_html()
        except ScraperError as error:
            return (False, self._error_policy.handle_exception(error, error))
        except (
            RequestError,
            ConnectionError,
            OSError,
            TimeoutError,
            RuntimeError,
        ) as exc:
            error = self._error_policy.wrap_network(exc)
            decision = self._error_policy.handle_recoverable_exception(
                exc=exc,
                error=error,
                attempt=attempt,
            )
            if decision == "retry":
                return (True, None)
            return (False, decision)
        else:
            self._logger.debug("Scrape run %s: finish download", run_id)
            self._quality_report_service.write_step(
                step_name="download",
                records=[],
            )
            return (False, html)

    def _parse_pipeline_with_error_handling(
        self,
        *,
        run_id: str,
        html: str,
    ) -> list[ExportRecord] | None:
        try:
            return self._pipeline_runner.run(run_id=run_id, html=html)
        except ScraperError as error:
            return self._error_policy.handle_exception(error, error)
        except (KeyError, ValueError) as exc:
            error = self._error_policy.wrap_parse(exc)
            return self._error_policy.handle_exception(exc, error)

    def _write_pipeline_quality_report(
        self,
        step_name: str,
        records: list[dict[str, object]],
    ) -> None:
        self._quality_report_service.write_step(step_name=step_name, records=records)

    def _write_pipeline_error_summary(self, payload: dict[str, object]) -> None:
        self._quality_report_service.write_error_summary(payload)

    @staticmethod
    def to_dict_records(records: list[ExportRecord]) -> list[dict[str, object]]:
        return to_dict_list(records)

    @staticmethod
    def build_validation_runner(
        *,
        validator: RecordValidator,
        validation_mode: str,
        logger,
        write_quality_report: Callable[[], None],
        url: str | None,
    ) -> ValidationRunner:
        return ValidationRunner(
            validator=validator,
            validation_mode=validation_mode,
            logger=logger,
            write_quality_report=write_quality_report,
            url=url,
        )
