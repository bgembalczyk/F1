from __future__ import annotations

import argparse
import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Type

from scrapers.base.exporters import ScrapeResult
from scrapers.base.scraper import F1Scraper


@dataclass(frozen=True)
class ScraperConfig:
    module_path: str
    class_name: str
    json_rel_path: Path
    csv_rel_path: Optional[Path]
    default_kwargs: Dict[str, Any]
    supports_urls: bool

SCRAPER_CONFIGS: Dict[str, ScraperConfig] = {
    "drivers": ScraperConfig(
        "scrapers.drivers.F1_drivers_list_scraper",
        "F1DriversListScraper",
        Path("drivers/f1_drivers.json"),
        Path("drivers/f1_drivers.csv"),
        {},
        supports_urls=True,
    ),
    "grands_prix": ScraperConfig(
        "scrapers.grands_prix.F1_grands_prix_list_scraper",
        "F1GrandsPrixListScraper",
        Path("grands_prix/f1_grands_prix_by_title.json"),
        Path("grands_prix/f1_grands_prix_by_title.csv"),
        {},
        supports_urls=True,
    ),
    "engine_manufacturers": ScraperConfig(
        "scrapers.engines.F1_engine_manufacturers_list_scraper",
        "F1EngineManufacturersListScraper",
        Path("engines/f1_engine_manufacturers.json"),
        Path("engines/f1_engine_manufacturers.csv"),
        {},
        supports_urls=True,
    ),
    "engine_manufacturers_indy": ScraperConfig(
        "scrapers.engines.F1_indianapolis_only_engine_manufacturers_list_scraper",
        "F1IndianapolisOnlyEngineManufacturersListScraper",
        Path("engines/f1_indianapolis_only_engine_manufacturers.json"),
        Path("engines/f1_indianapolis_only_engine_manufacturers.csv"),
        {},
        supports_urls=True,
    ),
    "constructors_2025": ScraperConfig(
        "scrapers.constructors.F1_constructors_2025_list_scraper",
        "F1Constructors2025ListScraper",
        Path("constructors/f1_constructors_2025.json"),
        Path("constructors/f1_constructors_2025.csv"),
        {},
        supports_urls=True,
    ),
    "constructors_former": ScraperConfig(
        "scrapers.constructors.F1_former_constructors_list_scraper",
        "F1FormerConstructorsListScraper",
        Path("constructors/f1_former_constructors.json"),
        Path("constructors/f1_former_constructors.csv"),
        {},
        supports_urls=True,
    ),
    "constructors_indy": ScraperConfig(
        "scrapers.constructors.F1_indianapolis_only_constructors_list_scraper",
        "F1IndianapolisOnlyConstructorsListScraper",
        Path("constructors/f1_indianapolis_only_constructors.json"),
        Path("constructors/f1_indianapolis_only_constructors.csv"),
        {},
        supports_urls=True,
    ),
    "constructors_privateer": ScraperConfig(
        "scrapers.constructors.F1_privateer_teams_list_scraper",
        "F1PrivateerTeamsListScraper",
        Path("constructors/f1_privateer_teams.json"),
        Path("constructors/f1_privateer_teams.csv"),
        {},
        supports_urls=True,
    ),
    "seasons": ScraperConfig(
        "scrapers.seasons.F1_seasons_list_scraper",
        "F1SeasonsListScraper",
        Path("seasons/f1_seasons.json"),
        Path("seasons/f1_seasons.csv"),
        {},
        supports_urls=True,
    ),
    "circuits": ScraperConfig(
        "scrapers.circuits.list_scraper",
        "F1CircuitsListScraper",
        Path("circuits/f1_circuits.json"),
        Path("circuits/f1_circuits.csv"),
        {},
        supports_urls=True,
    ),
    "circuits_complete": ScraperConfig(
        "scrapers.circuits.complete_scraper",
        "F1CompleteCircuitScraper",
        Path("circuits/f1_circuits_extended.json"),
        Path("circuits/f1_circuits_extended.csv"),
        {},
        supports_urls=True,
    ),
}


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def run_and_export(
    scraper_cls: Type[F1Scraper],
    json_path: str | Path,
    csv_path: str | Path | None = None,
    *,
    include_urls: bool = True,
    supports_urls: bool = True,
    **scraper_kwargs: Any,
) -> None:
    """
    Uruchamia scraper, a następnie zapisuje dane do JSON oraz CSV.

    - automatycznie przekazuje flagę ``include_urls`` (o ile scraper ją wspiera),
    - tworzy katalogi dla ścieżek wyjściowych,
    - wypisuje liczbę pobranych rekordów.
    """

    kwargs = dict(scraper_kwargs)
    if supports_urls and "include_urls" not in kwargs:
        kwargs["include_urls"] = include_urls

    scraper = scraper_cls(**kwargs)
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


def _load_scraper(module_path: str, class_name: str) -> Type[F1Scraper]:
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="Uruchamia wskazany scraper i zapisuje dane do JSON oraz CSV.",
    )
    parser.add_argument(
        "scraper",
        choices=sorted(SCRAPER_CONFIGS.keys()),
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

    config = SCRAPER_CONFIGS[args.scraper]
    scraper_cls = _load_scraper(config.module_path, config.class_name)
    kwargs = dict(config.default_kwargs)

    json_path = args.output_dir / config.json_rel_path
    csv_path = (
        args.output_dir / config.csv_rel_path
        if config.csv_rel_path is not None
        else None
    )

    run_and_export(
        scraper_cls,
        json_path,
        csv_path,
        include_urls=args.include_urls,
        supports_urls=config.supports_urls,
        **kwargs,
    )


if __name__ == "__main__":
    _cli()
