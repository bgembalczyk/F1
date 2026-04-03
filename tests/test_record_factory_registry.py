import pytest

from models.records.base_factory import BaseRecordFactory
from models.records.factories import registry
from models.records.factories.registry import CRITICAL_RECORD_TYPES
from models.records.factories.registry import FactoryRegistryProvider


def test_factory_registry_is_complete_for_critical_record_types() -> None:
    factory_registry = FactoryRegistryProvider().get()
    assert set(factory_registry) >= set(CRITICAL_RECORD_TYPES)


def test_factory_registry_has_unique_record_types() -> None:
    factory_registry = FactoryRegistryProvider().get()
    record_types = [factory.record_type for factory in factory_registry.values()]
    assert len(record_types) == len(set(record_types))


def test_build_factory_registry_no_duplicate_classes_after_reinit() -> None:
    first_registry = registry.build_factory_registry()
    second_registry = registry.build_factory_registry()

    assert len(first_registry) == len(second_registry)
    assert set(first_registry) == set(second_registry)


def test_build_factory_registry_order_and_content_are_deterministic() -> None:
    first_registry = registry.build_factory_registry()
    second_registry = registry.build_factory_registry()

    assert list(first_registry) == list(second_registry)
    assert set(first_registry) == set(second_registry)
    assert [type(factory) for factory in first_registry.values()] == [
        type(factory) for factory in second_registry.values()
    ]


def test_build_factory_registry_instances_are_isolated() -> None:
    first_registry = registry.build_factory_registry()
    second_registry = registry.build_factory_registry()

    assert first_registry is not second_registry
    assert set(first_registry) == set(second_registry)

    for record_type in first_registry:
        first_factory = first_registry[record_type]
        second_factory = second_registry[record_type]

        assert first_factory is not second_factory
        assert first_factory.normalizer is not second_factory.normalizer


def test_validate_factory_classes_raises_for_missing_critical_record_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _OnlyFactory(BaseRecordFactory):
        record_type = "non_critical"

    monkeypatch.setattr(
        registry,
        "CRITICAL_RECORD_TYPES",
        frozenset({"critical_missing_type"}),
    )

    with pytest.raises(
        registry.FactoryRegistryError,
        match="missing_critical_factory_record_types: critical_missing_type",
    ):
        registry._validate_factory_classes([_OnlyFactory])


def test_factory_registry_provider_uses_lazy_cache() -> None:
    provider = FactoryRegistryProvider()

    first = provider.get()
    second = provider.get()

    assert first is second


def test_factory_registry_provider_instances_are_isolated() -> None:
    first = FactoryRegistryProvider().get()
    second = FactoryRegistryProvider().get()

    assert first is not second
