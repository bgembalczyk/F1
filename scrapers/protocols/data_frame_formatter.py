from typing import Any
from typing import Protocol


class DataFrameFormatterProtocol(Protocol):
    def format(self, result) -> Any: ...
