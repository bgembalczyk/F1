from pathlib import Path
import inspect
from typing import Type

from scrapers.base.logging import get_logger
from scrapers.base.options import ScraperOptions
from scrapers.base.results import ScrapeResult
from scrapers.base.run_config import RunConfig
from scrapers.base.scraper import F1Scraper


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def supports_param(cls: type, param_name: str) -> bool:
    """True jeśli __init__ klasy przyjmuje parametr o nazwie param_name lub **kwargs."""
    try:
        sig = inspect.signature(cls.__init__)
    except (TypeError, ValueError):
        return False

    params = sig.parameters
    if param_name in params:
        return True
    return any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())


class ScraperRunner:
    """Orkiestruje tworzenie scrapera i eksport wyników."""

    def __init__(self, run_config: RunConfig, *, supports_urls: bool = True) -> None:
        self._run_config = run_config
        self._supports_urls = supports_urls

    def run_and_export(
        self,
        scraper_cls: Type[F1Scraper],
        json_rel: str | Path,
        csv_rel: str | Path | None = None,
    ) -> None:
        scraper = self._make_scraper(scraper_cls)
        data = scraper.fetch()

        scraper_logger = getattr(scraper, "logger", get_logger(scraper_cls.__name__))
        scraper_logger.info("Pobrano rekordów: %s", len(data))

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

    def _make_scraper(self, scraper_cls: Type[F1Scraper]) -> F1Scraper:
        """
        Tworzy instancję scrapera w sposób kompatybilny z różnymi konstruktorami:

        - jeśli scraper wspiera `options`, przekazujemy options
        - jeśli nie wspiera `options`, ale wspiera `include_urls`, to przekazujemy include_urls
        - jeśli supports_urls=False -> nie próbujemy ustawiać include_urls w ogóle
        """
        kwargs = dict(self._run_config.scraper_kwargs)
        options = self._run_config.options or ScraperOptions()
        if self._run_config.debug_dir is not None:
            options.debug_dir = self._run_config.debug_dir

        if supports_param(scraper_cls, "options"):
            if self._supports_urls and hasattr(options, "include_urls"):
                options.include_urls = self._run_config.include_urls
            kwargs.setdefault("options", options)
            return scraper_cls(**kwargs)

        if self._supports_urls and supports_param(scraper_cls, "include_urls"):
            kwargs.setdefault("include_urls", self._run_config.include_urls)

        return scraper_cls(**kwargs)
