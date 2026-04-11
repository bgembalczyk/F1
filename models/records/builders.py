from collections.abc import Callable
from collections.abc import Mapping
from functools import partial
from typing import Any
from typing import overload

from models.records.factories.protocol import RecordBuilder
from models.records.factories.registry.helpers import get_factory
from models.records.factories.registry.provider import FACTORY_REGISTRY_PROVIDER
from models.records.factories.registry.types import FactoryRegistry
from models.records.type import RecordType


class RecordBuilders:
    """Object facade for building normalized record models."""

    def __init__(
        self,
        factory_registry: FactoryRegistry | None = None,
    ):
        self._factory_registry = factory_registry or FACTORY_REGISTRY_PROVIDER.get()

    def _factory_for(self, record_type: RecordType | str) -> RecordBuilder:
        resolved_type = (
            record_type.value if isinstance(record_type, RecordType) else record_type
        )

        return get_factory(resolved_type, self._factory_registry)

    @overload
    def build(self, record_type: RecordType, record: Mapping[str, Any]) -> Any: ...

    @overload
    def build(self, record_type: str, record: Mapping[str, Any]) -> Any: ...

    def build(self, record_type: RecordType | str, record: Mapping[str, Any]) -> Any:
        return self._factory_for(record_type).build(record)

    def __getattr__(self, name: str) -> Callable[[Mapping[str, Any]], Any]:
        if name in RecordType._value2member_map_:
            return partial(self.build, RecordType(name))

        message = f"{self.__class__.__name__!s} has no attribute {name!r}"
        raise AttributeError(message)


RECORD_BUILDERS = RecordBuilders()
