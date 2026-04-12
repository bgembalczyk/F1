from abc import ABC

from scrapers.adapters.section.adapter import SectionAdapter
from scrapers.single_wiki_article.single_article_domain_scraper_base import (
    DomainArticleScraperBase,
)
from scrapers.single_wiki_article.single_article_section_aware_mixin import (
    SectionAwareMixin,
)


class SectionAdapterScraperBase(
    SectionAdapter,
    SectionAwareMixin,
    DomainArticleScraperBase,
    ABC,
):
    """Base for article scrapers that assemble records via SectionAdapter."""




__all__ = [
    "SectionAdapterScraperBase",
]
