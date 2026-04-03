from pathlib import Path
import warnings
from uuid import uuid4

from models.mappers.serialization import to_dict_list
from scrapers.base.abc import ABCScraper
from scrapers.base.factory.factory import ScraperFactory
from scrapers.base.helpers.path import ensure_parent
from scrapers.base.logging import get_logger
from scrapers.base.results import ScrapeResult
from scrapers.base.run_config import RunConfig
from scrapers.base.services.result_export_service import ResultExportService


class ScraperRunner:
    """Orkiestruje workflow uruchomienia scrapera i eksport wyników."""

    def __init__(
        self,
        run_config: RunConfig,
        *,
        supports_urls: bool = True,
        exporter: ResultExportService | None = None,
        result_export_service: ResultExportService | None = None,
    ) -> None:
        self._run_config = run_config
        self._supports_urls = supports_urls
        self._factory = ScraperFactory()
        self._exporter = exporter or result_export_service or ResultExportService()

    def run(
        self,
        scraper_cls: type[ABCScraper],
        json_rel: str | Path,
        csv_rel: str | Path | None = None,
    ) -> None:
        """Run workflow scrapera i zapisz wynik do JSON/CSV.

        Wejście: klasa scrapera oraz relatywne ścieżki wyjścia.
        Wyjście: brak (efekt uboczny: zapis plików).
        """
        run_id = uuid4().hex
        run_logger = get_logger(scraper_cls.__name__)
        run_logger.info("Scrape run %s started", run_id)
        scraper = self._create_scraper(scraper_cls, run_id=run_id)
        data = scraper.fetch()

        scraper_logger = getattr(scraper, "logger", run_logger)
        scraper_logger.info("Pobrano rekordów: %s (run_id=%s)", len(data), run_id)

        result = ScrapeResult(
            data=data,
            source_url=getattr(scraper, "url", None),
        )

        output_dir = Path(self._run_config.output_dir)
        json_path = output_dir / Path(json_rel)
        ensure_parent(json_path)
        self._exporter.to_json(
            result,
            json_path,
            exporter=scraper.exporter,
        )
        self._report_step(scraper, "export-json", data)

        if csv_rel:
            csv_path = output_dir / Path(csv_rel)
            ensure_parent(csv_path)
            self._exporter.to_csv(
                result,
                csv_path,
                exporter=scraper.exporter,
            )
            self._report_step(scraper, "export-csv", data)
        run_logger.info("Scrape run %s finished", run_id)

    def run_and_export(
        self,
        scraper_cls: type[ABCScraper],
        json_rel: str | Path,
        csv_rel: str | Path | None = None,
    ) -> None:
        """Deprecated alias for `run`.

        Wejście: klasa scrapera oraz relatywne ścieżki wyjścia.
        Wyjście: brak (efekt uboczny: zapis plików).
        """
        warnings.warn(
            "`run_and_export` is deprecated; use `run` for workflow execution.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.run(scraper_cls, json_rel, csv_rel)

    def _report_step(
        self,
        scraper: ABCScraper,
        step_name: str,
        data: list[object],
    ) -> None:
        step_report = getattr(scraper, "_write_step_quality_report", None)
        if not callable(step_report):
            return
        step_report(
            step_name=step_name,
            records=to_dict_list(list(data)),
        )

    def _create_scraper(
        self,
        scraper_cls: type[ABCScraper],
        *,
        run_id: str,
    ) -> ABCScraper:
        """Create instancję scrapera na podstawie klasy i run_id.

        Wejście: klasa scrapera oraz identyfikator uruchomienia.
        Wyjście: skonstruowana instancja `ABCScraper`.
        """
        return self._factory.create(
            scraper_cls=scraper_cls,
            run_config=self._run_config,
            run_id=run_id,
            supports_urls=self._supports_urls,
        )

    def _make_scraper(
        self,
        scraper_cls: type[ABCScraper],
        *,
        run_id: str,
    ) -> ABCScraper:
        """Deprecated alias for `_create_scraper`.

        Wejście: klasa scrapera oraz identyfikator uruchomienia.
        Wyjście: skonstruowana instancja `ABCScraper`.
        """
        warnings.warn(
            "`_make_scraper` is deprecated; use `_create_scraper`.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._create_scraper(scraper_cls, run_id=run_id)
