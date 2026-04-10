from collections.abc import Callable
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from warnings import warn


@dataclass(frozen=True, slots=True)
class CallableRecordFactoryAdapter:
    """Adapter for callable- and class-based legacy record factories."""

    factory: Callable[[dict[str, Any]], Any] | type

    def build(self, record: Mapping[str, Any]) -> Any:
        if isinstance(self.factory, type):
            return self.factory(**dict(record))
        return self.factory(dict(record))

    def create(self, payload: Mapping[str, Any]) -> Any:
        warn(
            "CallableRecordFactoryAdapter.create(payload) is deprecated; use build(record).",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.build(payload)
