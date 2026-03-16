from __future__ import annotations

from collections import Counter
from importlib import import_module
from pkgutil import iter_modules
from typing import TYPE_CHECKING
from typing import Final

from models.records.field_normalizer import FieldNormalizer

if TYPE_CHECKING:
    from models.records.base_factory import BaseRecordFactory


class FactoryRegistryError(ValueError):
    """Raised when record factory registry initialization fails."""


_REGISTERED_FACTORY_CLASSES: list[type[BaseRecordFactory]] = []
CRITICAL_RECORD_TYPES: Final[frozenset[str]] = frozenset(
    {
        "link",
        "season",
        "drivers_championships",
        "driver",
        "special_driver",
        "constructor",
        "circuit",
        "event",
        "car",
        "fatality",
        "season_summary",
        "grands_prix",
        "circuit_details",
        "circuit_complete",
        "engine_manufacturer",
    },
)


def register_factory(record_type: str | None = None):
    def decorator(factory_cls: type[BaseRecordFactory]) -> type[BaseRecordFactory]:
        class_record_type = getattr(factory_cls, "record_type", None)
        if not class_record_type:
            message = "factory_missing_record_type"
            raise FactoryRegistryError(message)
        if record_type and record_type != class_record_type:
            message = "factory_record_type_mismatch"
            raise FactoryRegistryError(message)
        _REGISTERED_FACTORY_CLASSES.append(factory_cls)
        return factory_cls

    return decorator


def _import_factory_modules() -> None:
    package = import_module("models.records.factories")
    for module_info in iter_modules(package.__path__):
        module_name = module_info.name
        if not module_name.endswith("_factory"):
            continue
        import_module(f"{package.__name__}.{module_name}")


def _validate_factory_classes(factory_classes: list[type[BaseRecordFactory]]) -> None:
    record_types = [factory_class.record_type for factory_class in factory_classes]
    duplicate_keys = sorted(
        record_type
        for record_type, count in Counter(record_types).items()
        if count > 1
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


def build_factory_registry(
    normalizer: FieldNormalizer | None = None,
) -> dict[str, BaseRecordFactory]:
    _import_factory_modules()
    factory_classes = list(_REGISTERED_FACTORY_CLASSES)
    _validate_factory_classes(factory_classes)

    shared_normalizer = normalizer or FieldNormalizer()
    return {
        factory_class.record_type: factory_class(shared_normalizer)
        for factory_class in factory_classes
    }


FACTORY_REGISTRY: Final[dict[str, BaseRecordFactory]] = build_factory_registry()
