from pathlib import Path
from uuid import uuid4

from scrapers.base.abc import F1Scraper
from scrapers.base.helpers.paremeters import supports_param
from scrapers.base.helpers.path import ensure_parent
from scrapers.base.logging import get_logger
from scrapers.base.options import ScraperOptions
from scrapers.base.results import ScrapeResult
from scrapers.base.run_config import RunConfig


class ScraperRunner:
    """Orkiestruje tworzenie scrapera i eksport wyników."""

    def __init__(self, run_config: RunConfig, *, supports_urls: bool = True) -> None:
        self._run_config = run_config
        self._supports_urls = supports_urls

    def run_and_export(
        self,
        scraper_cls: type[F1Scraper],
        json_rel: str | Path,
        csv_rel: str | Path | None = None,
    ) -> None:
        run_id = uuid4().hex
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
        ensure_parent(json_path)
        result.to_json(json_path, exporter=scraper.exporter)

        if csv_rel:
            csv_path = output_dir / Path(csv_rel)
            ensure_parent(csv_path)
            result.to_csv(csv_path, exporter=scraper.exporter)
        run_logger.info("Scrape run %s finished", run_id)

    def _make_scraper(self, scraper_cls: type[F1Scraper], *, run_id: str) -> F1Scraper:
        """
        Tworzy instancję scrapera w sposób kompatybilny z różnymi konstruktorami:

        - jeśli scraper wspiera `options`, przekazujemy options
        - jeśli nie wspiera `options`, ale wspiera `include_urls`,
          to przekazujemy include_urls
        - jeśli supports_urls=False -> nie próbujemy ustawiać include_urls w ogóle
        """
        kwargs = dict(self._run_config.scraper_kwargs)
        options = self._build_options(run_id)

        if supports_param(scraper_cls, "options"):
            self._inject_options_kwargs(kwargs, scraper_cls, options, run_id)
            return scraper_cls(**kwargs)

        self._inject_legacy_kwargs(kwargs, scraper_cls, run_id)
        return scraper_cls(**kwargs)

    def _build_options(self, run_id: str) -> ScraperOptions:
        options = self._run_config.options or ScraperOptions()
        options.run_id = run_id
        if self._run_config.debug_dir is not None:
            options.debug_dir = self._run_config.debug_dir
        if self._run_config.cache_dir is not None:
            options.cache_dir = self._run_config.cache_dir
        if self._run_config.cache_ttl is not None:
            options.cache_ttl = self._run_config.cache_ttl
        if self._run_config.cache_adapter is not None:
            options.cache_adapter = self._run_config.cache_adapter
        if self._run_config.http_timeout is not None:
            options.http_timeout = self._run_config.http_timeout
        if self._run_config.http_retries is not None:
            options.http_retries = self._run_config.http_retries
        if self._run_config.http_backoff_seconds is not None:
            options.http_backoff_seconds = self._run_config.http_backoff_seconds
        options.quality_report = self._run_config.quality_report
        options.error_report = self._run_config.error_report
        return options

    def _inject_options_kwargs(
        self,
        kwargs: dict[str, object],
        scraper_cls: type[F1Scraper],
        options: ScraperOptions,
        run_id: str,
    ) -> None:
        if self._supports_urls and hasattr(options, "include_urls"):
            options.include_urls = self._run_config.include_urls
        kwargs.setdefault("options", options)
        if supports_param(scraper_cls, "run_id"):
            kwargs.setdefault("run_id", run_id)

    def _inject_legacy_kwargs(
        self,
        kwargs: dict[str, object],
        scraper_cls: type[F1Scraper],
        run_id: str,
    ) -> None:
        if supports_param(scraper_cls, "run_id"):
            kwargs.setdefault("run_id", run_id)
        if self._supports_urls and supports_param(scraper_cls, "include_urls"):
            kwargs.setdefault("include_urls", self._run_config.include_urls)
