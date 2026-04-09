from models.records.factories.base import BaseRecordFactory
from models.records.factories.registry.helpers import build_factory_registry


class FactoryRegistryProvider:
    """Lazy provider with per-instance cache for built factory registry."""

    def __init__(self) -> None:
        self._registry: dict[str, BaseRecordFactory] | None = None

    def get(self) -> dict[str, BaseRecordFactory]:
        if self._registry is None:
            self._registry = build_factory_registry()
        return self._registry
