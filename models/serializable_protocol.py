from typing import Any
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class SerializableProtocol(Protocol):
    def to_serializable(self) -> Any: ...
