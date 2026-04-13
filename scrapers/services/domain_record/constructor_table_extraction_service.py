from __future__ import annotations

from typing import Any

from scrapers.mixins.run_diagnostics import RunDiagnosticsMixin
from scrapers.parsers.wiki.table.article_tables_assembler import ArticleTablesAssembler
from scrapers.parsers.wiki.table.article_tables_assembler_abc import (
    ArticleTablesAssemblerABC,
)


class ConstructorTableExtractionService(RunDiagnosticsMixin):
    """HTML adapter odpowiedzialny za ekstrakcję tabel dla konstruktorów."""

    def __init__(
        self,
        *,
        article_tables_assembler: ArticleTablesAssemblerABC | None = None,
    ) -> None:
        self._article_tables_assembler = (
            article_tables_assembler or ArticleTablesAssembler()
        )

    def extract_tables(self, soup: Any) -> list[dict[str, Any]]:
        return self.with_retry(lambda: self._article_tables_assembler.assemble(soup))
