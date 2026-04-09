from typing import Final

from models.records.factories.registry.provider import FactoryRegistryProvider

CRITICAL_RECORD_TYPES: Final[frozenset[str]] = frozenset(
    {
        "drivers_championships",
    },
)
FACTORY_MARKER_ATTR: Final[str] = "__factory_registry_record_type__"

FACTORY_REGISTRY_PROVIDER: Final[FactoryRegistryProvider] = FactoryRegistryProvider()
