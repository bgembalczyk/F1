from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any



class ArticleTablesParserABC(ABC):
    """Kontrakt parsera tabel całego artykułu."""

    # ARCH: To jedyny kontrakt parsera tabel artykułu (single source of truth).

    @abstractmethod
    def parse(self, element: Any) -> list[dict[str, Any]]: ...




__all__ = ["ArticleTablesParserABC"]
