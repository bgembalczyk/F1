from dataclasses import dataclass

from layers.seed.registry.entries.base import BaseRegistryEntry


@dataclass(frozen=True)
class SeedRegistryEntry(BaseRegistryEntry):
    default_output_path: str
    legacy_output_path: str
