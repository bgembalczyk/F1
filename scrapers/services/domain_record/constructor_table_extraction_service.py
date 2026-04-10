from __future__ import annotations

from typing import Any

from scrapers.mixins.pipeline_mixins import RetryMixin
from scrapers.parsers.table.wiki.article import ArticleTablesParser


class ConstructorTableExtractionService(RetryMixin):
    """HTML adapter odpowiedzialny za ekstrakcję tabel dla konstruktorów."""

    def __init__(
        self, *, article_tables_parser: ArticleTablesParser | None = None
    ) -> None:
        self._article_tables_parser = article_tables_parser or ArticleTablesParser()

    def extract_tables(self, soup: Any) -> list[dict[str, Any]]:
        return self.with_retry(lambda: self._article_tables_parser.parse(soup))
