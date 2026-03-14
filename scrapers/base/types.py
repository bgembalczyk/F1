from collections.abc import Iterable
from typing import Any
from typing import Protocol


class ExportableRecord(Protocol):
    def __getitem__(self, key: str) -> Any: ...

    def keys(self) -> Iterable[str]: ...

    def items(self) -> Iterable[tuple[str, Any]]: ...
