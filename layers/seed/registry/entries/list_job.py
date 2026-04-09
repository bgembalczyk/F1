from dataclasses import dataclass

from layers.seed.registry.entries.base import BaseRegistryEntry


@dataclass(frozen=True)
class ListJobRegistryEntry(BaseRegistryEntry):
    json_output_path: str
    legacy_json_output_path: str
    csv_output_path: str | None = None
