from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Type

from scrapers.base.logging import get_logger
from scrapers.base.options import ScraperOptions
from scrapers.base.results import ScrapeResult
from scrapers.base.scraper import F1Scraper


@dataclass(frozen=True)
class RunConfig:
    include_urls: bool = True
    output_dir: str | Path = Path(".")
    scraper_kwargs: dict[str, Any] = field(default_factory=dict)
    options: ScraperOptions | None = None


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
        _ensure_parent(json_path)
        result.to_json(json_path, exporter=scraper.exporter)

        if csv_rel:
            csv_path = output_dir / Path(csv_rel)
            _ensure_parent(csv_path)
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

        if _supports_param(scraper_cls, "options"):
            if self._supports_urls and hasattr(options, "include_urls"):
                options.include_urls = self._run_config.include_urls
            kwargs.setdefault("options", options)
            return scraper_cls(**kwargs)

        if self._supports_urls and _supports_param(scraper_cls, "include_urls"):
            kwargs.setdefault("include_urls", self._run_config.include_urls)

        return scraper_cls(**kwargs)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _supports_param(cls: type, param_name: str) -> bool:
    """
    True jeśli __init__ klasy przyjmuje param o nazwie param_name
    albo ma **kwargs (wtedy też możemy bezpiecznie podać).
    """
    try:
        sig = inspect.signature(cls.__init__)
    except (TypeError, ValueError):
        return False

    params = sig.parameters
    if param_name in params:
        return True
    return any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())


def run_and_export(
    scraper_cls: Type[F1Scraper],
    json_rel: str | Path,
    csv_rel: str | Path | None = None,
    *,
    run_config: RunConfig,
    supports_urls: bool = True,
) -> None:
    """
    Uruchamia scraper, a następnie zapisuje dane do JSON oraz CSV.

    - bezpiecznie przekazuje include_urls tylko jeśli ma sens,
    - wspiera scrapery na `options` oraz legacy konstruktory,
    - tworzy katalogi dla ścieżek wyjściowych,
    - wypisuje liczbę pobranych rekordów,
    - eksport obsługuje ScrapeResult.
    """
    runner = ScraperRunner(run_config, supports_urls=supports_urls)
    runner.run_and_export(scraper_cls, json_rel, csv_rel)
