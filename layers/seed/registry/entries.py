from dataclasses import asdict
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SeedRegistryEntry:
    seed_name: str
    wikipedia_url: str
    output_category: str
    list_scraper_cls: type[Any]
    default_output_path: str
    legacy_output_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ListJobRegistryEntry:
    seed_name: str
    wikipedia_url: str
    output_category: str
    list_scraper_cls: type[Any]
    json_output_path: str
    legacy_json_output_path: str
    csv_output_path: str | None = None
    requires_mirroring: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
