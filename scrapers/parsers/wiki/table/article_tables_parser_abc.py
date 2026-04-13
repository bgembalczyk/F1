"""Backward-compatibility shim: ArticleTablesParserABC has been removed.

Subclasses should inherit WikiArticleParserABC directly.
"""

from scrapers.parsers.contracts.wiki_elements import WikiArticleParserABC

#: Backward-compat alias.
ArticleTablesParserABC = WikiArticleParserABC

__all__ = ["ArticleTablesParserABC"]
