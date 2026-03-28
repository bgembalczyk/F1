from __future__ import annotations

from collections.abc import Callable
from typing import Any


class TableParserRegistry:
    """Registry mapujący table_type -> parser strategy."""

    def __init__(self) -> None:
        self._strategies: dict[str, Callable[..., Any]] = {}

    def register(self, table_type: str, strategy: Callable[..., Any]) -> None:
        self._strategies[table_type] = strategy

    def get(self, table_type: str) -> Callable[..., Any]:
        strategy = self._strategies.get(table_type)
        if strategy is None:
            msg = f"Unsupported table_type: {table_type}"
            raise ValueError(msg)
        return strategy

    def parse(self, table_type: str, **kwargs: Any) -> Any:
        return self.get(table_type)(**kwargs)
