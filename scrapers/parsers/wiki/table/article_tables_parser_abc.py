from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from scrapers.parsers.wiki.wiki_element_parser_abc import WikiArticleParserABC


class ArticleTablesParserABC(WikiArticleParserABC, ABC):
    """Kontrakt parsera tabel całego artykułu."""

    @abstractmethod
    def parse(self, element: Any) -> list[dict[str, Any]]: ...


__all__ = ["ArticleTablesParserABC"]
