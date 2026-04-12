from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from scrapers.parsers.roles import TableDomainMapperABC


class ArticleTablesParserABC(ABC):
    """Kontrakt parsera tabel całego artykułu."""

    @abstractmethod
    def parse(self, element: Any) -> list[dict[str, Any]]: ...




__all__ = ["ArticleTablesParserABC"]
