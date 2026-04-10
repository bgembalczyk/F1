from models.records.factories.registry.helpers import build_factory_registry
from models.records.factories.registry.types import MutableFactoryRegistry


class FactoryRegistryProvider:
    """Lazy provider with per-instance cache for built factory registry."""

    def __init__(self) -> None:
        self._registry: MutableFactoryRegistry | None = None

    def get(self) -> MutableFactoryRegistry:
        if self._registry is None:
            self._registry = build_factory_registry()
        return self._registry


FACTORY_REGISTRY_PROVIDER = FactoryRegistryProvider()
