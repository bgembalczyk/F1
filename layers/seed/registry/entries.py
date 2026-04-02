from dataclasses import asdict
from dataclasses import dataclass
from typing import Any

from layers.seed.registry.types import DomainName
from layers.seed.registry.types import SeedName


@dataclass(frozen=True)
class BaseRegistryEntry:
    seed_name: SeedName | str
    wikipedia_url: str
    output_category: DomainName
    list_scraper_cls: type[Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SeedRegistryEntry(BaseRegistryEntry):
    default_output_path: str
    legacy_output_path: str


@dataclass(frozen=True)
class ListJobRegistryEntry(BaseRegistryEntry):
    json_output_path: str
    legacy_json_output_path: str
    csv_output_path: str | None = None
