from collections.abc import Mapping
from typing import Any
from typing import Protocol


class RecordContract(Protocol):
    @classmethod
    def can_handle(cls, record: Mapping[str, Any]) -> bool: ...

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "DataContract": ...
