from __future__ import annotations

from typing import Callable, Dict, Iterable, Tuple

from scrapers.base.table.columns.types.base import BaseColumn

ColumnFactory = Callable[..., BaseColumn]


class ColumnTypeRegistry:
    def __init__(self) -> None:
        self._registry: Dict[str, ColumnFactory] = {}

    def register(self, key: str) -> Callable[[ColumnFactory], ColumnFactory]:
        normalized_key = key.strip().lower()

        def decorator(factory: ColumnFactory) -> ColumnFactory:
            self._registry[normalized_key] = factory
            return factory

        return decorator

    def get(self, key: str) -> ColumnFactory | None:
        return self._registry.get(key.strip().lower())

    def create(self, key: str, *args: object, **kwargs: object) -> BaseColumn:
        factory = self.get(key)
        if not factory:
            available = ", ".join(sorted(self._registry))
            raise KeyError(
                f"Unknown column type '{key}'. Available types: {available}"
            )
        return factory(*args, **kwargs)

    def entries(self) -> Iterable[Tuple[str, ColumnFactory]]:
        return self._registry.items()


column_type_registry = ColumnTypeRegistry()


def resolve_column_type(spec: BaseColumn | str) -> BaseColumn:
    if isinstance(spec, BaseColumn):
        return spec
    return column_type_registry.create(spec)
