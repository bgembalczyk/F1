from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from models.mappers.serialization import to_dict_list
from scrapers.base.abc import ABCScraper
from scrapers.base.factory.factory import ScraperFactory
from scrapers.base.logging import get_logger
from scrapers.base.results import ScrapeResult
from scrapers.base.run_config import RunConfig
from scrapers.base.services.result_export_service import ResultExportService


class ScraperRunner:
    """Orkiestruje tworzenie scrapera i eksport wyników."""

    def __init__(
        self,
        run_config: RunConfig,
        *,
        supports_urls: bool = True,
        run_id_provider: Callable[[], str] | None = None,
        exporter: ResultExportService | None = None,
        result_export_service: ResultExportService | None = None,
    ) -> None:
        self._run_config = run_config
        self._supports_urls = supports_urls
        self._factory = ScraperFactory()
        self._exporter = exporter or result_export_service or ResultExportService()
        self._run_id_provider = run_id_provider or (lambda: uuid4().hex)

    def run_and_export(
        self,
        scraper_cls: type[ABCScraper],
        json_rel: str | Path,
        csv_rel: str | Path | None = None,
    ) -> None:
        run_id = self._resolve_run_id(scraper_cls)
        run_logger = get_logger(scraper_cls.__name__)
        run_logger.info("Scrape run %s started", run_id)
        scraper = self._make_scraper(scraper_cls, run_id=run_id)
        data = scraper.fetch()

        scraper_logger = getattr(scraper, "logger", run_logger)
        scraper_logger.info("Pobrano rekordów: %s (run_id=%s)", len(data), run_id)

        result = ScrapeResult(
            data=data,
            source_url=getattr(scraper, "url", None),
        )

        output_dir = Path(self._run_config.output_dir)
        json_path = output_dir / Path(json_rel)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        self._exporter.to_json(
            result,
            json_path,
            exporter=scraper.exporter,
        )
        self._report_step(scraper, "export-json", data)

        if csv_rel:
            csv_path = output_dir / Path(csv_rel)
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            self._exporter.to_csv(
                result,
                csv_path,
                exporter=scraper.exporter,
            )
            self._report_step(scraper, "export-csv", data)
        run_logger.info("Scrape run %s finished", run_id)

    def _resolve_run_id(self, scraper_cls: type[ABCScraper]) -> str:
        if self._run_config.fixed_run_id:
            return self._run_config.fixed_run_id
        if self._run_config.deterministic_mode:
            return f"deterministic-{scraper_cls.__name__}"
        return self._run_id_provider()

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

    def _make_scraper(
        self,
        scraper_cls: type[ABCScraper],
        *,
        run_id: str,
    ) -> ABCScraper:
        return self._factory.create(
            scraper_cls=scraper_cls,
            run_config=self._run_config,
            run_id=run_id,
            supports_urls=self._supports_urls,
        )
