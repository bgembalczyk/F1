from typing import Any
from typing import Mapping
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class RecordFactoryProtocol(Protocol):
    """Structural protocol for all record factories registered in FACTORY_REGISTRY."""

    record_type: str

    def build(self, record: Mapping[str, Any]) -> Any: ...
