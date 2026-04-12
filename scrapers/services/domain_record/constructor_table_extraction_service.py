from __future__ import annotations

from typing import Any

from scrapers.mixins.run_diagnostics import RunDiagnosticsMixin
from scrapers.parsers.wiki.table.article import ArticleTablesParser
from scrapers.parsers.wiki.table.contracts import ArticleTablesParserABC


class ConstructorTableExtractionService(RunDiagnosticsMixin):
    """HTML adapter odpowiedzialny za ekstrakcję tabel dla konstruktorów."""

    def __init__(
        self,
        *,
        article_tables_parser: ArticleTablesParserABC | None = None,
    ) -> None:
        self._article_tables_parser = article_tables_parser or ArticleTablesParser()

    def extract_tables(self, soup: Any) -> list[dict[str, Any]]:
        return self.with_retry(lambda: self._article_tables_parser.parse(soup))
