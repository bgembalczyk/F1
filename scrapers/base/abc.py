from abc import ABC
from collections.abc import Callable
from collections.abc import Sequence
from pathlib import Path
from typing import TypeVar
from uuid import uuid4

from bs4 import BeautifulSoup

from infrastructure.http_client.policies.http import HttpPolicy
from models.mappers.serialization import to_dict_list
from scrapers.base.error_handler import ErrorHandler
from scrapers.base.errors import ScraperError
from scrapers.base.errors import ScraperNetworkError
from scrapers.base.errors import ScraperParseError
from scrapers.base.errors import ScraperValidationError
from scrapers.base.export.exporters import DataExporter
from scrapers.base.helpers.http import resolve_http_policy
from scrapers.base.helpers.source_adapter import build_source_adapter
from scrapers.base.helpers.transformers import build_transformers
from scrapers.base.helpers.url import normalize_url
from scrapers.base.logging import get_logger
from scrapers.base.normalization import RecordNormalizer
from scrapers.base.options import ScraperOptions
from scrapers.base.post_processors import apply_post_processors
from scrapers.base.quality.reporter import QualityReporter
from scrapers.base.records import NormalizedRecord
from scrapers.base.records import RawRecord
from scrapers.base.results import ScrapeResult
from scrapers.base.transformers.helpers import apply_transformers
from validation.validator_base import ExportRecord
from validation.validator_base import RecordValidator

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

        self.http_policy = self.get_http_policy(options)
        if self.http_policy is not None:
            options.policy = self.http_policy

        # Preferuj gotowy source_adapter w options.
        # HtmlFetcher jest config-driven, więc jeśli go nie ma,
        # tworzymy go "domyślnie".
        self.source_adapter = build_source_adapter(options, policy=self.http_policy)
        self.fetcher = options.fetcher

        # Parser może być zewnętrzny (np. mixin/adapter).
        self.parser = options.parser
        self.exporter = options.exporter or DataExporter()
        self._record_normalizer = RecordNormalizer(
            normalize_empty_values=self.normalize_empty_values,
        )
        self.transformers = build_transformers(options.transformers)
        self.post_processors = list(options.post_processors or [])
        self.logger = get_logger(self.__class__.__name__)
        self._error_handler = ErrorHandler(
            logger=self.logger,
            debug_dir=options.debug_dir,
            error_report_enabled=options.error_report,
            run_id=options.run_id,
        )
        self._run_id: str | None = options.run_id
        self.debug_dir = Path(options.debug_dir) if options.debug_dir else None
        self._quality_report_enabled = options.quality_report
        self._quality_reporter: QualityReporter | None = None

        if self._quality_report_enabled:
            self._quality_reporter = QualityReporter(
                report_root=self._resolve_quality_report_root(),
                run_id=self._run_id or "pending",
                source_metadata=self._source_metadata(),
            )

        self.validator: RecordValidator | None = options.validator or getattr(
            self,
            "default_validator",
            None,
        )
        if self.validator is not None:
            self.validator.set_record_factory(options.record_factory)
        self.validation_mode = options.validation_mode
        if self.validation_mode not in {"soft", "hard"}:
            msg = (
                "validation_mode must be 'soft' (drop record + warn) or 'hard' (raise)"
            )
            raise ValueError(
                msg,
            )

        self._data: list[ExportRecord] | None = None

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

        html = self._download_with_error_handling(run_id)
        if html is None:
            self._data = []
            return self._data

        data = self._parse_pipeline_with_error_handling(run_id, html)
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
        self._error_handler.set_run_id(run_id)
        self.logger.debug("Scrape run %s started for url=%s", run_id, self.url)
        return run_id

    def _download_with_error_handling(self, run_id: str) -> str | None:
        try:
            self.logger.debug("Scrape run %s: start download", run_id)
            html = self._download()
            self.logger.debug("Scrape run %s: finish download", run_id)
            self._write_step_quality_report(step_name="download", records=[])
            return html
        except Exception as exc:
            error: Exception
            if isinstance(exc, ScraperError):
                error = exc
            else:
                error = self._wrap_network_error(exc)
            return self._handle_fetch_error(exc, error)

    def _parse_pipeline_with_error_handling(
        self,
        run_id: str,
        html: str,
    ) -> list[ExportRecord] | None:
        try:
            return self._run_parse_pipeline(run_id, html)
        except Exception as exc:
            error = (
                exc if isinstance(exc, ScraperError) else self._wrap_parse_error(exc)
            )
            return self._handle_fetch_error(exc, error)

    def _run_parse_pipeline(self, run_id: str, html: str) -> list[ExportRecord]:
        soup = BeautifulSoup(html, "html.parser")

        self.logger.debug("Scrape run %s: start parse", run_id)
        raw_records = self.parse(soup)
        self.logger.debug("Scrape run %s: finish parse", run_id)
        self._write_step_quality_report(
            step_name="parse",
            records=list(raw_records),
        )

        self.logger.debug("Scrape run %s: start normalize", run_id)
        normalized_records = self._record_normalizer.normalize(list(raw_records))
        self.logger.debug("Scrape run %s: finish normalize", run_id)
        self._write_step_quality_report(
            step_name="normalize",
            records=to_dict_list(list(normalized_records)),
        )

        self.logger.debug("Scrape run %s: start transform", run_id)
        transformed_records = self._apply_transformers(normalized_records)
        self.logger.debug("Scrape run %s: finish transform", run_id)
        self._write_step_quality_report(
            step_name="transform",
            records=to_dict_list(list(transformed_records)),
        )

        self.logger.debug("Scrape run %s: start validate", run_id)
        validated_records = self.validate_records(transformed_records)
        self.logger.debug("Scrape run %s: finish validate", run_id)
        self._write_step_quality_report(
            step_name="validate",
            records=to_dict_list(list(validated_records)),
        )

        self.logger.debug("Scrape run %s: start post-process", run_id)
        post_processed = self.post_process_records(validated_records)
        self.logger.debug("Scrape run %s: finish post-process", run_id)
        self._write_step_quality_report(
            step_name="post_process",
            records=to_dict_list(list(post_processed)),
        )
        return post_processed

    def _handle_fetch_error(self, exc: Exception, error: Exception):
        if self._handle_scraper_error(error):
            return None
        if error is exc:
            raise
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

        self.validator.reset_stats()
        valid_records: list[ExportRecord] = []
        for index, record in enumerate(records):
            errors = self.validator.validate(record)
            record_factory_errors = self.validator.validate_record_factory(record)
            errors_for_tracking = list(errors)
            messages = [error.message for error in errors]
            if record_factory_errors:
                errors_for_tracking.extend(record_factory_errors)
                record_factory_label = (
                    getattr(self.validator.record_factory, "__name__", None)
                    if self.validator.record_factory is not None
                    else None
                )
                label = record_factory_label or "record_factory"
                messages.extend(
                    [f"{label}: {error.message}" for error in record_factory_errors],
                )
            self.validator.record_validation_result(errors_for_tracking)
            if not errors_for_tracking:
                valid_records.append(record)
                continue

            model_label = None
            if self.validator.record_factory is not None:
                model_label = getattr(self.validator.record_factory, "__name__", None)
                if model_label is None:
                    model_label = self.validator.record_factory.__class__.__name__

            message = (
                f"Validation failed for record #{index}"
                f"{f' ({model_label})' if model_label else ''} "
                f"with {len(errors_for_tracking)} error(s): {', '.join(messages)}"
            )
            if self.validation_mode == "soft":
                self.logger.warning(message)
                continue
            self._write_quality_report()
            raise ScraperValidationError(
                message=message,
                url=getattr(self, "url", None),
            )

        rejected = len(records) - len(valid_records)
        if rejected:
            self.logger.info(
                "Validation rejected %d record(s) out of %d",
                rejected,
                len(records),
            )
            self.logger.info(
                "Validation filtered records: %d -> %d",
                len(records),
                len(valid_records),
            )

        self._write_quality_report()
        return valid_records

    def _source_metadata(self) -> dict[str, object]:
        return {
            "domain": self.__module__.split(".")[1]
            if "." in self.__module__
            else self.__module__,
            "scraper": self.__class__.__name__,
            "scraper_kind": getattr(self, "scraper_kind", "single"),
            "url": getattr(self, "url", ""),
        }

    def _resolve_quality_report_root(self) -> Path:
        if self.debug_dir is not None:
            return self.debug_dir
        return Path("data/checkpoints")

    def _write_step_quality_report(
        self,
        *,
        step_name: str,
        records: list[dict[str, object]],
    ) -> None:
        if not self._quality_report_enabled or self._quality_reporter is None:
            return
        run_id = self._run_id or "no_run_id"
        self._quality_reporter.run_id = run_id
        step_id = f"{run_id}_{step_name}"
        report_path = self._quality_reporter.report_step(
            step_id=step_id,
            records=records,
            source_metadata=self._source_metadata(),
        )
        self.logger.debug("Saved step quality report: %s", report_path)

    def _write_quality_report(self) -> None:
        if (
            not self._quality_report_enabled
            or self.debug_dir is None
            or self.validator is None
        ):
            return
        report_path = self.validator.write_quality_report(self.debug_dir)
        self.logger.info("Saved quality report: %s", report_path)

    def _apply_transformers(self, records: list[ExportRecord]) -> list[ExportRecord]:
        return apply_transformers(self.transformers, records, logger=self.logger)

    # ---------- Pomocnicze ----------

    def _full_url(self, href: str) -> str | None:
        return normalize_url(self.url, href)

    def get_http_policy(self, options: ScraperOptions) -> HttpPolicy:
        return resolve_http_policy(options)

    # ---------- Error handling ----------

    def _wrap_network_error(self, exc: Exception) -> ScraperNetworkError:
        return self._error_handler.wrap_network(exc, url=getattr(self, "url", None))

    def _wrap_parse_error(self, exc: Exception) -> ScraperParseError:
        return self._error_handler.wrap_parse(exc, url=getattr(self, "url", None))

    def _handle_scraper_error(self, error: Exception) -> bool:
        return self._error_handler.handle(error)

    # ---------- Wspólne narzędzie do error handling ----------
    # Używane poza fetch(), np. w mixinach/infobox.

    def run_with_error_handling(
        self,
        fetch_fn: Callable[[], str],
        parse_fn: Callable[[BeautifulSoup], T],
        url: str,
    ) -> T | None:
        try:
            html = fetch_fn()
        except Exception as exc:
            error: Exception
            if isinstance(exc, ScraperError):
                error = exc
            else:
                error = self._wrap_network_error(exc)
            self._log_error_debug("network", url, error)
            if self._handle_scraper_error(error):
                return None
            if error is exc:
                raise
            raise error from exc

        try:
            soup = BeautifulSoup(html, "html.parser")
            return parse_fn(soup)
        except Exception as exc:
            error = (
                exc if isinstance(exc, ScraperError) else self._wrap_parse_error(exc)
            )
            self._log_error_debug("parse", url, error)
            if self._handle_scraper_error(error):
                return None
            if error is exc:
                raise
            raise error from exc

    def _log_error_debug(self, stage: str, url: str, error: Exception) -> None:
        self.logger.debug(
            "Scraper error in %s stage for url=%s (type=%s): %s",
            stage,
            url,
            type(error).__name__,
            error,
        )
