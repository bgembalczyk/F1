from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional, Sequence

from scrapers.base.scraper import F1Scraper
from scrapers.circuits.complete_scraper import F1CompleteCircuitScraper
from scrapers.circuits.list_scraper import F1CircuitsListScraper
from scrapers.constructors.F1_constructors_2025_list_scraper import (
    F1Constructors2025ListScraper,
)
from scrapers.constructors.F1_former_constructors_list_scraper import (
    F1FormerConstructorsListScraper,
)
from scrapers.constructors.F1_indianapolis_only_constructors_list_scraper import (
    F1IndianapolisOnlyConstructorsListScraper,
)
from scrapers.constructors.F1_privateer_teams_list_scraper import (
    F1PrivateerTeamsListScraper,
)
from scrapers.drivers.F1_drivers_list_scraper import F1DriversListScraper
from scrapers.engines.F1_engine_manufacturers_list_scraper import (
    F1EngineManufacturersListScraper,
)
from scrapers.engines.F1_indianapolis_only_engine_manufacturers_list_scraper import (
    F1IndianapolisOnlyEngineManufacturersListScraper,
)
from scrapers.grands_prix.F1_grands_prix_list_scraper import F1GrandsPrixListScraper
from scrapers.seasons.F1_seasons_list_scraper import F1SeasonsListScraper


@dataclass
class ScraperConfig:
    factory: Callable[[], F1Scraper]
    basename: str
    export_csv: bool = True
    fieldnames: Optional[Sequence[str]] = None


SCRAPERS: Dict[str, ScraperConfig] = {
    "drivers": ScraperConfig(
        factory=lambda: F1DriversListScraper(include_urls=True),
        basename="f1_drivers",
    ),
    "circuits": ScraperConfig(
        factory=lambda: F1CircuitsListScraper(include_urls=True),
        basename="f1_circuits",
    ),
    "circuits-extended": ScraperConfig(
        factory=lambda: F1CompleteCircuitScraper(delay_seconds=1.0),
        basename="f1_circuits_extended",
        export_csv=False,
    ),
    "grands-prix": ScraperConfig(
        factory=lambda: F1GrandsPrixListScraper(include_urls=True),
        basename="f1_grands_prix_by_title",
    ),
    "engines": ScraperConfig(
        factory=lambda: F1EngineManufacturersListScraper(include_urls=True),
        basename="f1_engine_manufacturers",
    ),
    "engines-indy": ScraperConfig(
        factory=lambda: F1IndianapolisOnlyEngineManufacturersListScraper(
            include_urls=True
        ),
        basename="f1_indianapolis_only_engine_manufacturers",
    ),
    "seasons": ScraperConfig(
        factory=lambda: F1SeasonsListScraper(include_urls=True),
        basename="f1_seasons",
    ),
    "constructors-2025": ScraperConfig(
        factory=lambda: F1Constructors2025ListScraper(include_urls=True),
        basename="f1_constructors_2025",
    ),
    "constructors-former": ScraperConfig(
        factory=lambda: F1FormerConstructorsListScraper(include_urls=True),
        basename="f1_former_constructors",
    ),
    "constructors-privateer": ScraperConfig(
        factory=lambda: F1PrivateerTeamsListScraper(include_urls=True),
        basename="f1_privateer_teams",
    ),
    "constructors-indy": ScraperConfig(
        factory=lambda: F1IndianapolisOnlyConstructorsListScraper(include_urls=True),
        basename="f1_indianapolis_only_constructors",
    ),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Uruchom wybrany scraper i zapisz dane do katalogu docelowego.",
    )
    parser.add_argument(
        "scraper",
        choices=SCRAPERS.keys(),
        help="Nazwa scrapera do uruchomienia (np. drivers, circuits, engines).",
    )
    parser.add_argument(
        "target_dir",
        help="Katalog docelowy, w którym zapisane zostaną pliki JSON/CSV.",
    )
    return parser


def run_scraper(scraper_key: str, target_dir: str | Path) -> Dict[str, Path]:
    if scraper_key not in SCRAPERS:
        available = ", ".join(sorted(SCRAPERS))
        raise SystemExit(f"Nieznany scraper '{scraper_key}'. Dostępne: {available}")

    config = SCRAPERS[scraper_key]
    scraper = config.factory()

    print(f"Uruchamiam scraper '{scraper_key}' -> {target_dir}")
    return scraper.export_data(
        target_dir,
        basename=config.basename,
        fieldnames=config.fieldnames,
        export_csv=config.export_csv,
    )


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    run_scraper(args.scraper, args.target_dir)


if __name__ == "__main__":
    main()
