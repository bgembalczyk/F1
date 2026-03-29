from dataclasses import asdict
from dataclasses import dataclass
from typing import Any

from layers.types import DomainName


@dataclass(frozen=True)
class BaseRegistryEntry:
    seed_name: str
    wikipedia_url: str
    output_category: DomainName
    list_scraper_cls: type[Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def domain(self) -> DomainName:
        return self.output_category


@dataclass(frozen=True)
class SeedRegistryEntry(BaseRegistryEntry):
    default_output_path: str
    legacy_output_path: str


@dataclass(frozen=True)
class ListJobRegistryEntry(BaseRegistryEntry):
    json_output_path: str
    legacy_json_output_path: str
    csv_output_path: str | None = None
