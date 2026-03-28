from abc import ABC

from scrapers.base.single_wiki_article.base import SingleWikiArticleScraperBase
from scrapers.base.single_wiki_article.strategies import SectionSelectionStrategy
from scrapers.base.single_wiki_article.strategies import UrlFragmentStrategy


class SingleWikiArticleSectionByIdBase(
    SingleWikiArticleScraperBase,
    ABC,
):
    """Wariant bazy z obsługą URL fragmentów i selekcji sekcji."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            url_fragment_strategy=UrlFragmentStrategy(),
            section_selection_strategy=SectionSelectionStrategy(),
            **kwargs,
        )

    def _uses_url_fragment(self) -> bool:
        return True
