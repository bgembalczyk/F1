from collections.abc import Callable
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CallableRecordFactoryAdapter:
    """Adapter for callable- and class-based legacy record factories."""

    factory: Callable[[dict[str, Any]], Any] | type

    def create(self, payload: Mapping[str, Any]) -> Any:
        if isinstance(self.factory, type):
            return self.factory(**dict(payload))
        return self.factory(dict(payload))
