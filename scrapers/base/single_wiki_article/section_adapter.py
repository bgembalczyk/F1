from abc import ABC

from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.single_wiki_article.base import SingleWikiArticleScraperBase


class SingleWikiArticleSectionAdapterBase(
    SectionAdapter,
    SingleWikiArticleScraperBase,
    ABC,
):
    """Wariant dla scraperów opartych o ``SectionAdapter``."""
