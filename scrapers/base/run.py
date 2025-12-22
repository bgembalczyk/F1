from __future__ import annotations

import argparse
import inspect
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Type

from scrapers.base.options import ScraperOptions
from scrapers.base.registry import (
    SCRAPER_REGISTRY,
    load_default_scrapers,
    ScraperRegistryConfig,
)
from scrapers.base.results import ScrapeResult
from scrapers.base.scraper import F1Scraper

from scrapers.base.logging import configure_logging, get_logger


@dataclass(frozen=True)
class RunConfig:
    include_urls: bool = True
    output_dir: str | Path = Path(".")
    scraper_kwargs: dict[str, Any] = field(default_factory=dict)
    options: ScraperOptions | None = None


def _scraper_choices() -> list[str]:
    load_default_scrapers()
    return sorted(SCRAPER_REGISTRY.keys())


def _get_scraper_config(name: str) -> ScraperRegistryConfig:
    load_default_scrapers()
    return SCRAPER_REGISTRY[name]


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


def _make_scraper(
    scraper_cls: Type[F1Scraper],
    *,
    include_urls: bool,
    supports_urls: bool,
    options: ScraperOptions,
    kwargs: dict[str, Any],
) -> F1Scraper:
    """
    Tworzy instancję scrapera w sposób kompatybilny z różnymi konstruktorami:

    - jeśli scraper wspiera `options`, przekazujemy options
    - jeśli nie wspiera `options`, ale wspiera `include_urls`, to przekazujemy include_urls jako kwarg
    - jeśli supports_urls=False -> nie próbujemy ustawiać include_urls w ogóle
    """
    ctor_kwargs = dict(kwargs)

    if _supports_param(scraper_cls, "options"):
        # Scraper może (ale nie musi) używać include_urls z options.
        if supports_urls and hasattr(options, "include_urls"):
            options.include_urls = include_urls
        ctor_kwargs.setdefault("options", options)
        return scraper_cls(**ctor_kwargs)

    # Brak parametru "options" -> ewentualnie include_urls jako kwarg,
    # ale tylko jeśli:
    # - caller mówi, że ma to sens (supports_urls=True),
    # - scraper to przyjmuje (albo ma **kwargs).
    if supports_urls and _supports_param(scraper_cls, "include_urls"):
        ctor_kwargs.setdefault("include_urls", include_urls)

    return scraper_cls(**ctor_kwargs)


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
    kwargs = dict(run_config.scraper_kwargs)
    options = run_config.options or ScraperOptions()

    scraper = _make_scraper(
        scraper_cls,
        include_urls=run_config.include_urls,
        supports_urls=supports_urls,
        options=options,
        kwargs=kwargs,
    )

    data = scraper.fetch()

    scraper_logger = getattr(scraper, "logger", get_logger(scraper_cls.__name__))
    scraper_logger.info("Pobrano rekordów: %s", len(data))

    result = ScrapeResult(
        data=data,
        source_url=getattr(scraper, "url", None),
    )

    output_dir = Path(run_config.output_dir)
    json_path = output_dir / Path(json_rel)
    _ensure_parent(json_path)
    result.to_json(json_path, exporter=scraper.exporter)

    if csv_rel:
        csv_path = output_dir / Path(csv_rel)
        _ensure_parent(csv_path)
        result.to_csv(csv_path, exporter=scraper.exporter)


def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="Uruchamia wskazany scraper i zapisuje dane do JSON oraz CSV.",
    )
    parser.add_argument(
        "scraper",
        choices=_scraper_choices(),
        help="Nazwa scrapera (klucz z SCRAPER_REGISTRY).",
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Katalog bazowy, w którym powstaną pliki (np. data/wiki).",
    )
    parser.add_argument(
        "--no-urls",
        dest="include_urls",
        action="store_false",
        help="Wyłącza zbieranie URL-i tam, gdzie scraper to wspiera.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Poziom logowania (domyślnie: INFO).",
    )
    parser.set_defaults(include_urls=True)
    args = parser.parse_args()

    configure_logging(args.log_level)

    config = _get_scraper_config(args.scraper)
    scraper_cls = config.scraper_cls
    kwargs = dict(getattr(config, "default_kwargs", {}) or {})

    # kompatybilność z różnymi nazwami w configu (na przyszłość)
    json_rel = getattr(config, "json_rel", None) or getattr(
        config, "json_rel_path", None
    )
    csv_rel = getattr(config, "csv_rel", None) or getattr(config, "csv_rel_path", None)

    if json_rel is None:
        raise RuntimeError(f"Config dla {args.scraper!r} nie ma json_rel/json_rel_path")

    supports_urls = getattr(config, "supports_urls", True)

    run_config = RunConfig(
        include_urls=args.include_urls,
        output_dir=args.output_dir,
        scraper_kwargs=kwargs,
    )

    run_and_export(
        scraper_cls,
        json_rel,
        csv_rel,
        run_config=run_config,
        supports_urls=supports_urls,
    )


if __name__ == "__main__":
    _cli()
