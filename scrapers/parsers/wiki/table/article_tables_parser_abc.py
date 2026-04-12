from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any



class ArticleTablesParserABC(ABC):
    """Kontrakt parsera tabel całego artykułu."""

    @abstractmethod
    def parse(self, element: Any) -> list[dict[str, Any]]: ...




__all__ = ["ArticleTablesParserABC"]
