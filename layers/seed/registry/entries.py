from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BaseRegistryEntry:
    seed_name: str
    wikipedia_url: str
    output_category: str
    list_scraper_cls: type[Any]


@dataclass(frozen=True)
class SeedRegistryEntry(BaseRegistryEntry):
    default_output_path: str
    legacy_output_path: str


@dataclass(frozen=True)
class ListJobRegistryEntry(BaseRegistryEntry):
    json_output_path: str
    legacy_json_output_path: str
    csv_output_path: str | None = None
