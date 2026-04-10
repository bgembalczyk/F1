from abc import ABC

from scrapers.adapters.section.adapter import SectionAdapter
from scrapers.single_wiki_article.base import SingleWikiArticleScraperBase


class SingleWikiArticleSectionAdapterBase(
    SectionAdapter,
    SingleWikiArticleScraperBase,
    ABC,
):
    """Wariant dla scraperów opartych o ``SectionAdapter``."""


__all__ = ["SingleWikiArticleSectionAdapterBase"]
