from abc import ABC

from scrapers.base.single_wiki_article.base import SingleWikiArticleScraperBase
from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)


class SingleWikiArticleSectionByIdBase(SingleWikiArticleScraperBase, ABC):
    """Backward-compatible baza używająca strategii sekcji po identyfikatorze."""

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault(
            "section_selection_strategy",
            WikipediaSectionByIdSelectionStrategy(),
        )
        super().__init__(*args, **kwargs)
