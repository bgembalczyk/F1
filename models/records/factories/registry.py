from __future__ import annotations

from collections import Counter
from functools import cache
from importlib import import_module
from pkgutil import iter_modules
from typing import TYPE_CHECKING
from typing import Final
from typing import cast

from models.records.field_normalizer import FieldNormalizer

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Iterator
    from collections.abc import Mapping

    from models.records.base_factory import BaseRecordFactory


class FactoryRegistryError(ValueError):
    """Raised when record factory registry initialization fails."""


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


class FactoryRegistry:
    """Explicit registry of initialized record factories."""

    def __init__(self, factories: Mapping[str, BaseRecordFactory] | None = None):
        self._factories = dict(factories or {})

    def get(self, record_type: str) -> BaseRecordFactory | None:
        return self._factories.get(record_type)

    def items(self) -> Iterator[tuple[str, BaseRecordFactory]]:
        return iter(self._factories.items())

    def keys(self) -> Iterator[str]:
        return iter(self._factories.keys())

    def values(self) -> Iterator[BaseRecordFactory]:
        return iter(self._factories.values())

    def __contains__(self, record_type: object) -> bool:
        return record_type in self._factories

    def __iter__(self) -> Iterator[str]:
        return iter(self._factories)

    def __len__(self) -> int:
        return len(self._factories)


class FactoryRegistryBootstrap:
    """Collects factory classes before building a concrete registry."""

    def __init__(self) -> None:
        self._factory_classes: list[type[BaseRecordFactory]] = []

    def register_factory_class(
        self,
        factory_cls: type[BaseRecordFactory],
        *,
        record_type: str | None = None,
    ) -> type[BaseRecordFactory]:
        class_record_type = getattr(factory_cls, "record_type", None)
        if not class_record_type:
            message = "factory_missing_record_type"
            raise FactoryRegistryError(message)
        if record_type and record_type != class_record_type:
            message = "factory_record_type_mismatch"
            raise FactoryRegistryError(message)
        self._factory_classes.append(factory_cls)
        return factory_cls

    def registered_factory_classes(self) -> list[type[BaseRecordFactory]]:
        return list(self._factory_classes)

    def build_registry(
        self,
        normalizer: FieldNormalizer | None = None,
        *,
        validate_critical: bool = True,
    ) -> FactoryRegistry:
        factory_classes = self.registered_factory_classes()
        _validate_factory_classes(
            factory_classes,
            validate_critical=validate_critical,
        )

        shared_normalizer = normalizer or FieldNormalizer()
        return FactoryRegistry(
            {
                factory_class.record_type: factory_class(shared_normalizer)
                for factory_class in factory_classes
            },
        )


def register_factory(
    record_type: str | None = None,
    *,
    bootstrap: FactoryRegistryBootstrap | None = None,
):
    registry_bootstrap = bootstrap or DEFAULT_FACTORY_BOOTSTRAP

    def decorator(factory_cls: type[BaseRecordFactory]) -> type[BaseRecordFactory]:
        return registry_bootstrap.register_factory_class(
            factory_cls,
            record_type=record_type,
        )

    return decorator


def _iter_factory_module_names(
    package_name: str = "models.records.factories",
) -> Iterable[str]:
    package = import_module(package_name)
    for module_info in iter_modules(package.__path__):
        module_name = module_info.name
        if module_name.endswith("_factory"):
            yield f"{package.__name__}.{module_name}"


def import_factory_modules(module_names: Iterable[str] | None = None) -> None:
    names = module_names or _iter_factory_module_names()
    for module_name in names:
        import_module(module_name)


def _validate_factory_classes(
    factory_classes: list[type[BaseRecordFactory]],
    *,
    validate_critical: bool = True,
) -> None:
    record_types = [factory_class.record_type for factory_class in factory_classes]
    duplicate_keys = sorted(
        record_type for record_type, count in Counter(record_types).items() if count > 1
    )
    if duplicate_keys:
        message = "duplicate_factory_record_types: " + ", ".join(duplicate_keys)
        raise FactoryRegistryError(message)

    if not validate_critical:
        return

    missing_critical = sorted(CRITICAL_RECORD_TYPES - set(record_types))
    if missing_critical:
        message = "missing_critical_factory_record_types: " + ", ".join(
            missing_critical,
        )
        raise FactoryRegistryError(message)


def build_factory_registry(
    normalizer: FieldNormalizer | None = None,
    *,
    bootstrap: FactoryRegistryBootstrap | None = None,
    module_names: Iterable[str] | None = None,
    import_modules: bool = True,
    validate_critical: bool = True,
) -> FactoryRegistry:
    if import_modules:
        import_factory_modules(module_names)
    registry_bootstrap = bootstrap or DEFAULT_FACTORY_BOOTSTRAP
    return registry_bootstrap.build_registry(
        normalizer,
        validate_critical=validate_critical,
    )


DEFAULT_FACTORY_BOOTSTRAP: Final[FactoryRegistryBootstrap] = FactoryRegistryBootstrap()


@cache
def get_default_factory_registry() -> FactoryRegistry:
    return cast("FactoryRegistry", build_factory_registry())
