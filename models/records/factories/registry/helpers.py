from __future__ import annotations

from collections import Counter
from importlib import import_module
from inspect import isclass
from pkgutil import iter_modules

from models.records.factories.base import BaseRecordFactory
from models.records.factories.protocol import RecordBuilder
from models.records.factories.registry.constants import CRITICAL_RECORD_TYPES
from models.records.factories.registry.constants import FACTORY_MARKER_ATTR
from models.records.factories.registry.constants import FACTORY_REGISTRY_PROVIDER
from models.records.factories.registry.error import FactoryRegistryError
from models.records.factories.registry.types import MutableFactoryRegistry
from models.records.field_normalizer import FieldNormalizer


def register_factory(record_type: str | None = None):
    def decorator(factory_cls: type[BaseRecordFactory]) -> type[BaseRecordFactory]:
        class_record_type = getattr(factory_cls, "record_type", None)
        if not class_record_type:
            message = "factory_missing_record_type"
            raise FactoryRegistryError(message)
        if record_type and record_type != class_record_type:
            message = "factory_record_type_mismatch"
            raise FactoryRegistryError(message)
        setattr(factory_cls, FACTORY_MARKER_ATTR, class_record_type)
        return factory_cls

    return decorator


def import_factory_modules() -> list[object]:
    package = import_module("models.records.factories")
    imported_modules: list[object] = []
    for module_info in iter_modules(package.__path__):
        module_name = module_info.name
        if not module_name.endswith("_factory"):
            continue
        imported_modules.append(import_module(f"{package.__name__}.{module_name}"))
    return imported_modules


def collect_registered_factory_classes() -> list[type[BaseRecordFactory]]:
    factory_classes: list[type[BaseRecordFactory]] = []
    for module in import_factory_modules():
        for candidate in vars(module).values():
            if not isclass(candidate):
                continue
            if getattr(candidate, "__module__", None) != module.__name__:
                continue
            if getattr(candidate, FACTORY_MARKER_ATTR, None) is None:
                continue
            factory_classes.append(candidate)
    return factory_classes


def validate_factory_classes(factory_classes: list[type[BaseRecordFactory]]) -> None:
    record_types = [factory_class.record_type for factory_class in factory_classes]
    duplicate_keys = sorted(
        record_type for record_type, count in Counter(record_types).items() if count > 1
    )
    if duplicate_keys:
        message = "duplicate_factory_record_types: " + ", ".join(duplicate_keys)
        raise FactoryRegistryError(message)

    missing_critical = sorted(CRITICAL_RECORD_TYPES - set(record_types))
    if missing_critical:
        message = "missing_critical_factory_record_types: " + ", ".join(
            missing_critical,
        )
        raise FactoryRegistryError(message)


def get_factory(
    record_type: str,
    registry: MutableFactoryRegistry | None = None,
) -> RecordBuilder:
    factory_registry = registry or FACTORY_REGISTRY_PROVIDER.get()
    factory = factory_registry.get(record_type)
    if factory is None:
        msg = f"Unsupported record type: {record_type}"
        raise ValueError(msg)
    return factory


def build_factory_registry(
    normalizer: FieldNormalizer | None = None,
) -> MutableFactoryRegistry:
    factory_classes = collect_registered_factory_classes()
    validate_factory_classes(factory_classes)

    shared_normalizer = normalizer or FieldNormalizer()
    return {
        factory_class.record_type: factory_class(shared_normalizer)
        for factory_class in factory_classes
    }





__all__ = [
    "build_factory_registry",
    "collect_registered_factory_classes",
    "get_factory",
    "import_factory_modules",
    "register_factory",
    "validate_factory_classes",
]
