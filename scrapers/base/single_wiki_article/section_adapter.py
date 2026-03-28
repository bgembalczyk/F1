from abc import ABC

from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.single_wiki_article.base import SingleWikiArticleScraperBase
from scrapers.base.single_wiki_article.strategies import SectionSelectionStrategy
from scrapers.base.single_wiki_article.strategies import UrlFragmentStrategy


class SingleWikiArticleSectionAdapterBase(
    SingleWikiArticleScraperBase,
    ABC,
):
    """Wariant dla scraperów opartych o ``SectionAdapter``."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            url_fragment_strategy=UrlFragmentStrategy(),
            section_selection_strategy=SectionSelectionStrategy(),
            **kwargs,
        )
        self._section_adapter = SectionAdapter()

    def parse_sections(self, **kwargs):
        return self._section_adapter.parse_sections(**kwargs)

    def parse_section_dicts(self, **kwargs):
        return self._section_adapter.parse_section_dicts(**kwargs)

    def fetch_by_url(self, url: str) -> list[dict[str, object]]:
        return SingleWikiArticleScraperBase.fetch_by_url(self, url)

    def _uses_url_fragment(self) -> bool:
        """Czy ``fetch_by_url`` powinien obsługiwać URL z fragmentem sekcji."""
        return False
