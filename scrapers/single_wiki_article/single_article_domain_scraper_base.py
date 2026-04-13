"""Backward-compatibility shim. DomainArticleScraperBase is now ArticleScraperBase."""

from scrapers.single_wiki_article.single_article_scraper_base import ArticleScraperBase

DomainArticleScraperBase = ArticleScraperBase

__all__ = ["DomainArticleScraperBase"]
