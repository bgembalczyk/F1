from models.records.factories.registry import CRITICAL_RECORD_TYPES
from models.records.factories.registry import FactoryRegistryProvider


def test_factory_registry_is_complete_for_critical_record_types() -> None:
    factory_registry = FactoryRegistryProvider().get()
    assert set(factory_registry) >= set(CRITICAL_RECORD_TYPES)


def test_factory_registry_has_unique_record_types() -> None:
    factory_registry = FactoryRegistryProvider().get()
    record_types = [factory.record_type for factory in factory_registry.values()]
    assert len(record_types) == len(set(record_types))


def test_factory_registry_provider_uses_lazy_cache() -> None:
    provider = FactoryRegistryProvider()

    first = provider.get()
    second = provider.get()

    assert first is second


def test_factory_registry_provider_instances_are_isolated() -> None:
    first = FactoryRegistryProvider().get()
    second = FactoryRegistryProvider().get()

    assert first is not second
