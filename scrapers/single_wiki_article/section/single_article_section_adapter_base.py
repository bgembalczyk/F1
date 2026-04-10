from abc import ABC

from scrapers.adapters.section.adapter import SectionAdapter
from scrapers.single_wiki_article.single_article_domain_scraper_base import (
    SingleArticleDomainScraperBase,
)


class SingleArticleSectionAdapterBase(
    SectionAdapter,
    SingleArticleDomainScraperBase,
    ABC,
):
    """Wariant dla scraperów opartych o ``SectionAdapter``."""

    FAMILY_KIND = "single_article"


class SingleWikiArticleSectionAdapterBase(SingleArticleSectionAdapterBase):
    """Backward-compatible alias for legacy naming."""

    FAMILY_KIND = "single_article"


__all__ = [
    "SingleArticleSectionAdapterBase",
    "SingleWikiArticleSectionAdapterBase",
]
