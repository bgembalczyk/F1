from models.records.base_factory import BaseRecordFactory
from models.records.factories.build import build_record
from models.records.factories.registry import CRITICAL_RECORD_TYPES
from models.records.factories.registry import FactoryRegistryBootstrap
from models.records.factories.registry import build_factory_registry
from models.records.factories.registry import get_default_factory_registry
from models.records.factories.registry import register_factory


def test_factory_registry_is_complete_for_critical_record_types() -> None:
    registry = get_default_factory_registry()
    assert set(registry) >= set(CRITICAL_RECORD_TYPES)


def test_factory_registry_has_unique_record_types() -> None:
    registry = get_default_factory_registry()
    record_types = [factory.record_type for factory in registry.values()]
    assert len(record_types) == len(set(record_types))


def test_factory_registry_can_be_built_without_global_state() -> None:
    bootstrap = FactoryRegistryBootstrap()

    @register_factory("custom", bootstrap=bootstrap)
    class CustomRecordFactory(BaseRecordFactory):
        record_type = "custom"

        def build(self, record):
            return {"value": record["value"].strip()}

    registry = build_factory_registry(
        bootstrap=bootstrap,
        import_modules=False,
        validate_critical=False,
    )

    assert build_record("custom", {"value": "  ok  "}, registry=registry) == {
        "value": "ok",
    }
