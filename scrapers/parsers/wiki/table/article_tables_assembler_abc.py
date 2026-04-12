from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any


class ArticleTablesAssemblerABC(ABC):
    """Kontrakt assemblera tabel całego artykułu."""

    @abstractmethod
    def assemble(self, element: Any) -> list[dict[str, Any]]: ...


__all__ = ["ArticleTablesAssemblerABC"]
