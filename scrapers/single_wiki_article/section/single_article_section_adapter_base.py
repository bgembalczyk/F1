"""Backward-compatibility shim: SectionAdapterScraperBase has been removed.

Subclasses should inherit directly from SectionAdapter, SectionAwareMixin, and ArticleScraperBase.
"""

from abc import ABC

from scrapers.adapters.section.adapter import SectionAdapter
from scrapers.single_wiki_article.single_article_scraper_base import ArticleScraperBase
from scrapers.single_wiki_article.single_article_section_aware_mixin import (
    SectionAwareMixin,
)


class SectionAdapterScraperBase(
    SectionAdapter,
    SectionAwareMixin,
    ArticleScraperBase,
    ABC,
):
    """Backward-compat alias. Inherit SectionAdapter, SectionAwareMixin, ArticleScraperBase directly."""


__all__ = [
    "SectionAdapterScraperBase",
]
