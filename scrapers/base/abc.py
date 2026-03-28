from abc import ABC
from collections.abc import Callable
from collections.abc import Sequence
from pathlib import Path
import warnings
from typing import TypeVar
from uuid import uuid4

from bs4 import BeautifulSoup

from infrastructure.http_client.policies.http import HttpPolicy
from scrapers.base.errors import ScraperError
from scrapers.base.errors import ScraperNetworkError
from scrapers.base.errors import ScraperParseError
from scrapers.base.helpers.http import resolve_http_policy
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
from scrapers.base.transformers.helpers import apply_transformers
from scrapers.base.transformers.stages import TransformerStage
from scrapers.base.validation_runner import ValidationRunner
from validation.validator_base import ExportRecord

T = TypeVar("T")


class ABCScraper(ABC):
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

    #: Pełny URL strony (ustawiany w klasach potomnych)
    url: str

    def __init__(self, *, options: ScraperOptions) -> None:
        self.include_urls = options.include_urls
        self.normalize_empty_values = options.normalize_empty_values
        self.logger = get_logger(self.__class__.__name__)
        self._run_id: str | None = options.run_id
        self.debug_dir = Path(options.debug_dir) if options.debug_dir else None
        self._quality_report_enabled = options.quality_report
        self._validation_mode = "soft"
        self._initialize_runtime(options)
        self._validate_validation_mode()
        self._initialize_quality_report_service()
        self._initialize_pipeline_orchestrator()
        self._data: list[ExportRecord] | None = None

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
        self._error_policy = ErrorPolicy(
            error_handler=runtime.error_handler,
            logger=self.logger,
            get_url=lambda: getattr(self, "url", None),
        )

    def _initialize_quality_report_service(self) -> None:
        self._quality_report_service = QualityReportService(
            enabled=self._quality_report_enabled,
            debug_dir=self.debug_dir,
            run_id=self._run_id,
            source_metadata_provider=self._source_metadata,
            logger=self.logger,
            validator_provider=lambda: self.validator,
        )

    def _initialize_pipeline_orchestrator(self) -> None:
        self._pipeline_orchestrator = PipelineOrchestrator(
            logger=self.logger,
            quality_report_service=self._quality_report_service,
            error_policy=self._error_policy,
            parse_records=self.parse,
            normalize_records=self._normalize_pipeline_records,
            transform_records=self._apply_transformers,
            validate_records=self.validate_records,
            post_process_records=self.post_process_records,
        )

    def _validate_validation_mode(self) -> None:
        if self._validation_mode in {"soft", "hard"}:
            return
        msg = "validation_mode must be 'soft' (drop record + warn) or 'hard' (raise)"
        raise ValueError(msg)

    @property
    def validation_mode(self) -> str:
        return self._validation_mode

    @validation_mode.setter
    def validation_mode(self, value: str) -> None:
        self._validation_mode = value

    # ---------- API wysokiego poziomu ----------

    def fetch(self) -> list[ExportRecord]:
        """
        Pobierz HTML i sparsuj do listy rekordów eksportowych.

        Pipeline:
        - download
        - parse -> RawRecord[]
        - RecordNormalizer.normalize -> NormalizedRecord[]
        - transformers -> ExportRecord[]

        Error handling:
        - ScraperError z critical=True -> propagujemy
        - pozostałe -> warning + soft-skip (puste dane)

        Zwraca zawsze listę ExportRecord (może być pusta).
        """
        self._validate_fetch_url()
        run_id = self._start_run()
        data = self._pipeline_orchestrator.run_fetch(
            run_id=run_id,
            download_html=self._download,
        )
        if data is None:
            return self._store_empty_data()

        return self._assemble_fetch_result(run_id, data)

    def _store_empty_data(self) -> list[ExportRecord]:
        self._data = []
        return self._data

    def _assemble_fetch_result(
        self,
        run_id: str,
        data: list[ExportRecord],
    ) -> list[ExportRecord]:
        self._data = data
        self.logger.debug("Scrape run %s finished", run_id)
        return self._data

    def _finalize_fetch(
        self,
        run_id: str,
        data: list[ExportRecord],
    ) -> list[ExportRecord]:
        warnings.warn(
            "ABCScraper._finalize_fetch() is deprecated; use "
            "_assemble_fetch_result() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._assemble_fetch_result(run_id, data)

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

    def _download_with_error_handling(self, run_id: str) -> str | None:
        try:
            self.logger.debug("Scrape run %s: start download", run_id)
            html = self._download()
            self.logger.debug("Scrape run %s: finish download", run_id)
            self._write_step_quality_report(step_name="download", records=[])
        except ScraperError as error:
            return self._handle_fetch_error(error, error)
        except (RuntimeError, ValueError, OSError) as exc:
            error = self._wrap_network_error(exc)
            return self._handle_fetch_error(exc, error)
        else:
            return html

    def _parse_pipeline_with_error_handling(
        self,
        run_id: str,
        html: str,
    ) -> list[ExportRecord] | None:
        try:
            return self._run_parse_pipeline(run_id, html)
        except ScraperError as error:
            return self._handle_fetch_error(error, error)
        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
            error = self._wrap_parse_error(exc)
            return self._handle_fetch_error(exc, error)

    def _build_pipeline_runner(self) -> ScraperPipelineRunner:
        return ScraperPipelineRunner(
            logger=self.logger,
            write_step_quality_report=self._write_pipeline_quality_report,
            parse_records=self.parse,
            normalize_records=self._normalize_pipeline_records,
            pre_validate_transform_records=lambda records: self._apply_transformers_for_stage(
                records,
                TransformerStage.PRE_VALIDATE,
            ),
            enrich_records=lambda records: self._apply_transformers_for_stage(
                records,
                TransformerStage.ENRICH,
            ),
            validate_records=self.validate_records,
            post_validate_transform_records=lambda records: self._apply_transformers_for_stage(
                records,
                TransformerStage.POST_VALIDATE,
            ),
            post_process_records=self.post_process_records,
        )

    def _run_parse_pipeline(self, run_id: str, html: str) -> list[ExportRecord]:
        return self._pipeline_runner.run(run_id=run_id, html=html)

    def _normalize_pipeline_records(
        self,
        records: list[RawRecord],
    ) -> list[NormalizedRecord]:
        return self._record_normalizer.normalize(records)

    def _apply_transformers_for_stage(
        self,
        records: list[ExportRecord],
        stage: TransformerStage,
    ) -> list[ExportRecord]:
        scoped = [
            transformer
            for transformer in self.transformers
            if getattr(transformer, "stage", TransformerStage.ENRICH) == stage
        ]
        if not scoped:
            return records
        return apply_transformers(scoped, records, logger=self.logger)

    def _write_pipeline_quality_report(
        self,
        step_name: str,
        records: list[dict[str, object]],
    ) -> None:
        self._write_step_quality_report(step_name=step_name, records=records)

    def _handle_fetch_error(self, exc: Exception, error: ScraperError):
        if self._handle_scraper_error(error):
            return
        if error is exc:
            raise exc
        raise error from exc

    def get_data(self) -> list[ExportRecord]:
        """Zwróć dane - jeśli jeszcze nie ma, uruchom fetch()."""
        if self._data is None:
            return self.fetch()
        return self._data

    def build_result(self, data: list[ExportRecord] | None = None) -> ScrapeResult:
        """Utwórz ScrapeResult z metadanymi."""
        return ScrapeResult(
            data=data if data is not None else self.get_data(),
            source_url=getattr(self, "url", None),
        )

    # ---------- Eksport (delegowany) ----------

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

    # ---------- Metody wewnętrzne ----------

    def _download(self) -> str:
        # Adapter jest jedyną “bramką” do źródła (może być CacheAdapter).
        return self.fetch_html(self.url)

    def fetch_html(self, url: str) -> str:
        return self.source_adapter.get(url)

    def _parse_soup(self, _soup: BeautifulSoup) -> list[RawRecord]:
        """Parsowanie BS4 -> lista rekordów surowych."""
        msg = (
            f"{self.__class__.__name__} must implement _parse_soup() "
            "or override parse()."
        )
        raise NotImplementedError(
            msg,
        )

    def parse(self, soup: BeautifulSoup) -> list[RawRecord]:
        if self.parser is None:
            return self._parse_soup(soup)
        return self.parser.parse(soup)

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

    def _source_metadata(self) -> dict[str, object]:
        return {
            "domain": self.__module__.split(".")[1]
            if "." in self.__module__
            else self.__module__,
            "scraper": self.__class__.__name__,
            "scraper_kind": getattr(self, "scraper_kind", "single"),
            "url": getattr(self, "url", ""),
        }

    def _write_step_quality_report(
        self,
        *,
        step_name: str,
        records: list[dict[str, object]],
    ) -> None:
        self._quality_report_service.write_step(step_name=step_name, records=records)

    def _write_quality_report(self) -> None:
        self._quality_report_service.write_validation_report()

    def _apply_transformers(self, records: list[ExportRecord]) -> list[ExportRecord]:
        return apply_transformers(self.transformers, records, logger=self.logger)

    # ---------- Pomocnicze ----------

    def _full_url(self, href: str) -> str | None:
        return normalize_url(self.url, href)

    def get_http_policy(self, options: ScraperOptions) -> HttpPolicy:
        return resolve_http_policy(options)

    # ---------- Error handling ----------

    def _wrap_network_error(self, exc: Exception) -> ScraperNetworkError:
        return self._error_policy.wrap_network(exc)

    def _wrap_parse_error(self, exc: Exception) -> ScraperParseError:
        return self._error_policy.wrap_parse(exc)

    def _handle_scraper_error(self, error: ScraperError) -> bool:
        return self._error_policy.handle(error)

    # ---------- Wspólne narzędzie do error handling ----------
    # Używane poza fetch(), np. w mixinach/infobox.

    def run_with_error_handling(
        self,
        fetch_fn: Callable[[], str],
        parse_fn: Callable[[BeautifulSoup], T],
        url: str,
    ) -> T | None:
        html = self._run_fetch_stage(fetch_fn, url)
        if html is None:
            return None
        return self._run_parse_stage(parse_fn, url, html)

    def _run_fetch_stage(self, fetch_fn: Callable[[], str], url: str) -> str | None:
        try:
            return fetch_fn()
        except Exception as exc:  # noqa: BLE001
            return self._handle_stage_error(
                stage="network",
                url=url,
                exc=exc,
                error=self._network_stage_error(exc),
            )

    def _run_parse_stage(
        self,
        parse_fn: Callable[[BeautifulSoup], T],
        url: str,
        html: str,
    ) -> T | None:
        try:
            soup = BeautifulSoup(html, "html.parser")
            return parse_fn(soup)
        except Exception as exc:  # noqa: BLE001
            return self._handle_stage_error(
                stage="parse",
                url=url,
                exc=exc,
                error=self._parse_stage_error(exc),
            )

    def _network_stage_error(self, exc: Exception) -> ScraperError:
        if isinstance(exc, ScraperError):
            return exc
        return self._wrap_network_error(exc)

    def _parse_stage_error(self, exc: Exception) -> ScraperError:
        if isinstance(exc, ScraperError):
            return exc
        return self._wrap_parse_error(exc)

    def _handle_stage_error(
        self,
        *,
        stage: str,
        url: str,
        exc: Exception,
        error: ScraperError,
    ) -> None:
        if self._handle_scraper_error(error):
            return
        if error is exc:
            raise exc
        raise error from exc
