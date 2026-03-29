from __future__ import annotations

from collections import Counter
from importlib import import_module
from inspect import isclass
from pkgutil import iter_modules
from typing import TYPE_CHECKING
from typing import Final

from models.records.field_normalizer import FieldNormalizer

if TYPE_CHECKING:
    from models.records.base_factory import BaseRecordFactory


class FactoryRegistryError(ValueError):
    """Raised when record factory registry initialization fails."""


CRITICAL_RECORD_TYPES: Final[frozenset[str]] = frozenset(
    {
        "drivers_championships",
    },
)
FACTORY_MARKER_ATTR: Final[str] = "__factory_registry_record_type__"


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


def _import_factory_modules() -> list[object]:
    package = import_module("models.records.factories")
    imported_modules: list[object] = []
    for module_info in iter_modules(package.__path__):
        module_name = module_info.name
        if not module_name.endswith("_factory"):
            continue
        imported_modules.append(import_module(f"{package.__name__}.{module_name}"))
    return imported_modules


def _collect_registered_factory_classes() -> list[type[BaseRecordFactory]]:
    factory_classes: list[type[BaseRecordFactory]] = []
    for module in _import_factory_modules():
        for candidate in vars(module).values():
            if not isclass(candidate):
                continue
            if getattr(candidate, "__module__", None) != module.__name__:
                continue
            if getattr(candidate, FACTORY_MARKER_ATTR, None) is None:
                continue
            factory_classes.append(candidate)
    return factory_classes


def _validate_factory_classes(factory_classes: list[type[BaseRecordFactory]]) -> None:
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
    registry: dict[str, BaseRecordFactory] | None = None,
) -> BaseRecordFactory:
    factory_registry = registry or FACTORY_REGISTRY_PROVIDER.get()
    factory = factory_registry.get(record_type)
    if factory is None:
        msg = f"Unsupported record type: {record_type}"
        raise ValueError(msg)
    return factory


def build_factory_registry(
    normalizer: FieldNormalizer | None = None,
) -> dict[str, BaseRecordFactory]:
    factory_classes = _collect_registered_factory_classes()
    _validate_factory_classes(factory_classes)

    shared_normalizer = normalizer or FieldNormalizer()
    return {
        factory_class.record_type: factory_class(shared_normalizer)
        for factory_class in factory_classes
    }


class FactoryRegistryProvider:
    """Lazy provider with per-instance cache for built factory registry."""

    def __init__(self) -> None:
        self._registry: dict[str, BaseRecordFactory] | None = None

    def get(self) -> dict[str, BaseRecordFactory]:
        if self._registry is None:
            self._registry = build_factory_registry()
        return self._registry


FACTORY_REGISTRY_PROVIDER: Final[FactoryRegistryProvider] = FactoryRegistryProvider()
