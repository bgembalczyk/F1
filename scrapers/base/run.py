from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Type

from scrapers.base.exporters import ScrapeResult
from scrapers.base.registry import (
    SCRAPER_REGISTRY,
    ScraperConfig,
    load_default_scrapers,
)
from scrapers.base.options import ScraperOptions
from scrapers.base.scraper import F1Scraper


def _scraper_choices() -> list[str]:
    load_default_scrapers()
    return sorted(SCRAPER_REGISTRY.keys())


def _get_scraper_config(name: str) -> ScraperConfig:
    load_default_scrapers()
    return SCRAPER_REGISTRY[name]


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def run_and_export(
    scraper_cls: Type[F1Scraper],
    json_path: str | Path,
    csv_path: str | Path | None = None,
    *,
    include_urls: bool = True,
    **scraper_kwargs: Any,
) -> None:
    """
    Uruchamia scraper, a następnie zapisuje dane do JSON oraz CSV.

    - automatycznie przekazuje flagę ``include_urls`` (o ile scraper ją wspiera),
    - tworzy katalogi dla ścieżek wyjściowych,
    - wypisuje liczbę pobranych rekordów.
    """

    kwargs = dict(scraper_kwargs)
    options = kwargs.pop("options", None)
    if options is None:
        options = ScraperOptions()
    options.include_urls = include_urls

    scraper = scraper_cls(options=options, **kwargs)
    data = scraper.fetch()

    print(f"Pobrano rekordów: {len(data)}")

    result = ScrapeResult(data=data, source_url=getattr(scraper, "url", None))

    json_path = Path(json_path)
    _ensure_parent(json_path)
    scraper.exporter.to_json(result, json_path)

    if csv_path:
        csv_path = Path(csv_path)
        _ensure_parent(csv_path)
        scraper.exporter.to_csv(result, csv_path)


def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="Uruchamia wskazany scraper i zapisuje dane do JSON oraz CSV.",
    )
    parser.add_argument(
        "scraper",
        choices=_scraper_choices(),
        help="Nazwa scrappera (klucz z konfiguracji w scrapers/base/run.py)",
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
    parser.set_defaults(include_urls=True)
    args = parser.parse_args()

    config = _get_scraper_config(args.scraper)
    scraper_cls = config.scraper_cls
    kwargs = dict(config.default_kwargs)

    json_path = args.output_dir / config.json_rel
    csv_path = args.output_dir / config.csv_rel if config.csv_rel is not None else None

    run_and_export(
        scraper_cls,
        json_path,
        csv_path,
        include_urls=args.include_urls,
        **kwargs,
    )


if __name__ == "__main__":
    _cli()
