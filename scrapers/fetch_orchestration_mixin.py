from uuid import uuid4

from scrapers.options import ScraperOptions
from scrapers.runners.pipeline_runner import NormalizedRecord
from scrapers.runners.pipeline_runner import RawRecord
from scrapers.scraper_components import ErrorPolicy
from scrapers.scraper_components import PipelineOrchestrator
from scrapers.scraper_components import RuntimeInitializer
from validation.validator_base import ExportRecord


class FetchOrchestrationMixin:
    """Fetch orchestration and runtime wiring mixin (stateless business-wise)."""

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
            parse_records=self.parse_soup,
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
        self._reporting_service.set_run_context(run_id)
        self._reporting_service.log_start(self.url)
        return run_id

    def _normalize_pipeline_records(
        self,
        records: list[RawRecord],
    ) -> list[NormalizedRecord]:
        return self._record_normalizer.normalize(records)
