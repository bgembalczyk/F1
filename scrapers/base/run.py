from __future__ import annotations

import argparse
import inspect
from pathlib import Path
from typing import Any, Type

from scrapers.base.options import ScraperOptions
from scrapers.base.registry import SCRAPER_REGISTRY, ScraperConfig, load_default_scrapers
from scrapers.base.results import ScrapeResult
from scrapers.base.scraper import F1Scraper

# Logging (z PR). Jeśli moduł nie istnieje w repo, fallback na print.
from scrapers.base.logging import configure_logging, logger  # type: ignore



def _scraper_choices() -> list[str]:
    load_default_scrapers()
    return sorted(SCRAPER_REGISTRY.keys())


def _get_scraper_config(name: str) -> ScraperConfig:
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


def _write_json(result: ScrapeResult, *, scraper: F1Scraper, path: Path) -> None:
    """
    Kompatybilność eksportu między:
    - nowym API (jeśli kiedyś będzie): result.to_json(path)
    - obecnym API: scraper.exporter.to_json(result, path)
    """
    if hasattr(result, "to_json") and callable(getattr(result, "to_json")):
        result.to_json(path)  # type: ignore[call-arg]
        return
    scraper.exporter.to_json(result, path)


def _write_csv(result: ScrapeResult, *, scraper: F1Scraper, path: Path) -> None:
    """
    Kompatybilność eksportu między:
    - nowym API (jeśli kiedyś będzie): result.to_csv(path)
    - obecnym API: scraper.exporter.to_csv(result, path)
    """
    if hasattr(result, "to_csv") and callable(getattr(result, "to_csv")):
        result.to_csv(path)  # type: ignore[call-arg]
        return
    scraper.exporter.to_csv(result, path)


def run_and_export(
    scraper_cls: Type[F1Scraper],
    json_path: str | Path,
    csv_path: str | Path | None = None,
    *,
    include_urls: bool = True,
    supports_urls: bool = True,
    options: ScraperOptions | None = None,
    **scraper_kwargs: Any,
) -> None:
    """
    Uruchamia scraper, a następnie zapisuje dane do JSON oraz CSV.

    - bezpiecznie przekazuje include_urls tylko jeśli ma sens,
    - wspiera scrapery na `options` oraz legacy konstruktory,
    - tworzy katalogi dla ścieżek wyjściowych,
    - wypisuje liczbę pobranych rekordów,
    - wspiera 2 style eksportu (result.to_* oraz exporter.to_*(result,...)).
    """
    kwargs = dict(scraper_kwargs)
    options = options or ScraperOptions()

    scraper = _make_scraper(
        scraper_cls,
        include_urls=include_urls,
        supports_urls=supports_urls,
        options=options,
        kwargs=kwargs,
    )

    data = scraper.fetch()

    if logger is not None:
        logger.info("Pobrano rekordów: %s", len(data))
    else:
        print(f"Pobrano rekordów: {len(data)}")

    result = ScrapeResult(
        data=data,
        source_url=getattr(scraper, "url", None),
    )

    json_path = Path(json_path)
    _ensure_parent(json_path)
    _write_json(result, scraper=scraper, path=json_path)

    if csv_path:
        csv_path = Path(csv_path)
        _ensure_parent(csv_path)
        _write_csv(result, scraper=scraper, path=csv_path)


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
    json_rel = getattr(config, "json_rel", None) or getattr(config, "json_rel_path", None)
    csv_rel = getattr(config, "csv_rel", None) or getattr(config, "csv_rel_path", None)

    if json_rel is None:
        raise RuntimeError(f"Config dla {args.scraper!r} nie ma json_rel/json_rel_path")

    json_path = args.output_dir / Path(json_rel)
    csv_path = args.output_dir / Path(csv_rel) if csv_rel is not None else None

    supports_urls = getattr(config, "supports_urls", True)

    run_and_export(
        scraper_cls,
        json_path,
        csv_path,
        include_urls=args.include_urls,
        supports_urls=supports_urls,
        **kwargs,
    )


if __name__ == "__main__":
    _cli()
