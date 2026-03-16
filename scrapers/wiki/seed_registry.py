from dataclasses import asdict
from dataclasses import dataclass
from typing import Any

from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.constructors.current_constructors_list import (
    CurrentConstructorsListScraper,
)
from scrapers.drivers.list_scraper import F1DriversListScraper
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper
from scrapers.seasons.list_scraper import SeasonsListScraper


@dataclass(frozen=True)
class SeedRegistryEntry:
    seed_name: str
    wikipedia_url: str
    output_category: str
    list_scraper_cls: type[Any]
    default_output_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


WIKI_SEED_REGISTRY: tuple[SeedRegistryEntry, ...] = (
    SeedRegistryEntry(
        seed_name="drivers",
        wikipedia_url=F1DriversListScraper.CONFIG.url,
        output_category="drivers",
        list_scraper_cls=F1DriversListScraper,
        default_output_path="drivers/complete_drivers",
    ),
    SeedRegistryEntry(
        seed_name="constructors",
        wikipedia_url=CurrentConstructorsListScraper.CONFIG.url,
        output_category="constructors",
        list_scraper_cls=CurrentConstructorsListScraper,
        default_output_path="constructors/complete_constructors",
    ),
    SeedRegistryEntry(
        seed_name="grands_prix",
        wikipedia_url=GrandsPrixListScraper.CONFIG.url,
        output_category="grands_prix",
        list_scraper_cls=GrandsPrixListScraper,
        default_output_path="grands_prix/f1_grands_prix_extended.json",
    ),
    SeedRegistryEntry(
        seed_name="circuits",
        wikipedia_url=CircuitsListScraper.CONFIG.url,
        output_category="circuits",
        list_scraper_cls=CircuitsListScraper,
        default_output_path="circuits/complete_circuits",
    ),
    SeedRegistryEntry(
        seed_name="seasons",
        wikipedia_url=SeasonsListScraper.CONFIG.url,
        output_category="seasons",
        list_scraper_cls=SeasonsListScraper,
        default_output_path="seasons/complete_seasons",
    ),
)


def validate_seed_registry(
    registry: tuple[SeedRegistryEntry, ...] = WIKI_SEED_REGISTRY,
) -> None:
    seen_seed_names: set[str] = set()

    for entry in registry:
        if entry.seed_name in seen_seed_names:
            msg = f"Duplicate seed_name found: {entry.seed_name}"
            raise ValueError(msg)
        seen_seed_names.add(entry.seed_name)

        if not entry.wikipedia_url.strip():
            msg = f"Seed '{entry.seed_name}' has empty wikipedia_url"
            raise ValueError(msg)

        expected_prefix = f"{entry.output_category}/"
        if not entry.default_output_path.startswith(expected_prefix):
            msg = (
                f"Seed '{entry.seed_name}' has inconsistent output path "
                f"'{entry.default_output_path}' for category '{entry.output_category}'"
            )
            raise ValueError(msg)
