from __future__ import annotations

import argparse
from pathlib import Path

from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.registry import (
    SCRAPER_REGISTRY,
    load_default_scrapers,
    ScraperRegistryConfig,
)
from scrapers.base.logging import configure_logging


def _scraper_choices() -> list[str]:
    load_default_scrapers()
    return sorted(SCRAPER_REGISTRY.keys())


def _get_scraper_config(name: str) -> ScraperRegistryConfig:
    load_default_scrapers()
    return SCRAPER_REGISTRY[name]


def run_scraper_by_name(
    name: str,
    output_dir: str | Path,
    *,
    include_urls: bool = True,
    log_level: str | None = None,
) -> None:
    if log_level:
        configure_logging(log_level)

    config = _get_scraper_config(name)
    scraper_cls = config.scraper_cls
    kwargs = dict(getattr(config, "default_kwargs", {}) or {})

    # kompatybilność z różnymi nazwami w configu (na przyszłość)
    json_rel = getattr(config, "json_rel", None) or getattr(
        config, "json_rel_path", None
    )
    csv_rel = getattr(config, "csv_rel", None) or getattr(config, "csv_rel_path", None)

    if json_rel is None:
        raise RuntimeError(f"Config dla {name!r} nie ma json_rel/json_rel_path")

    supports_urls = getattr(config, "supports_urls", True)

    run_config = RunConfig(
        include_urls=include_urls,
        output_dir=output_dir,
        scraper_kwargs=kwargs,
    )

    run_and_export(
        scraper_cls,
        json_rel,
        csv_rel,
        run_config=run_config,
        supports_urls=supports_urls,
    )


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

    run_scraper_by_name(
        args.scraper,
        args.output_dir,
        include_urls=args.include_urls,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    _cli()
