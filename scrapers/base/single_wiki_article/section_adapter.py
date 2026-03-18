from abc import ABC

from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.single_wiki_article.base import SingleWikiArticleScraperBase


class SingleWikiArticleSectionAdapterBase(
    SectionAdapter,
    SingleWikiArticleScraperBase,
    ABC,
):
    """Wariant dla scraperów opartych o ``SectionAdapter``."""

    def fetch_by_url(self, url: str) -> list[dict[str, object]]:
        if self._uses_url_fragment():
            return WikipediaSectionByIdMixin.fetch_by_url(self, url)
        return SingleWikiArticleScraperBase.fetch_by_url(self, url)

    def _uses_url_fragment(self) -> bool:
        """Czy ``fetch_by_url`` powinien obsługiwać URL z fragmentem sekcji."""
        return False
