from models.records.factories.registry import CRITICAL_RECORD_TYPES
from models.records.factories.registry import FACTORY_REGISTRY


def test_factory_registry_is_complete_for_critical_record_types() -> None:
    assert set(FACTORY_REGISTRY) >= set(CRITICAL_RECORD_TYPES)


def test_factory_registry_has_unique_record_types() -> None:
    record_types = [factory.record_type for factory in FACTORY_REGISTRY.values()]
    assert len(record_types) == len(set(record_types))
