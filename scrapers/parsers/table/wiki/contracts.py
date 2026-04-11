from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class WikiTableDomainMapper(Protocol):
    """Kontrakt mapowania parsera tabel wiki na rekordy domenowe."""

    def parse(self, fragment: dict[str, Any]) -> dict[str, Any] | None: ...


@runtime_checkable
class ArticleTablesParserProtocol(Protocol):
    """Kontrakt parsera tabel całego artykułu."""

    def parse(self, element: Any) -> list[dict[str, Any]]: ...


__all__ = ["ArticleTablesParserProtocol", "WikiTableDomainMapper"]
