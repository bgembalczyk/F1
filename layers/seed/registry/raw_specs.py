from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RawRegistrySpec:
    seed_name: str
    list_scraper_cls: type[Any]
    output_category: str
    list_filename: str
    seed_filename: str | None = None
    seed_output_category: str | None = None
    list_output_category: str | None = None
    include_in_list_registry: bool = True
