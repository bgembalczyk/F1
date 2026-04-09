from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BaseRegistryEntry:
    seed_name: str
    wikipedia_url: str
    output_category: str
    list_scraper_cls: type[Any]
