from abc import ABC

from scrapers.base.single_wiki_article import WikipediaSectionByIdSelectionStrategy
from scrapers.base.single_wiki_article.base import SingleWikiArticleScraperBase


class SingleWikiArticleSectionByIdBase(SingleWikiArticleScraperBase, ABC):
    """Backward-compatible baza używająca strategii sekcji po identyfikatorze."""

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault(
            "section_selection_strategy",
            WikipediaSectionByIdSelectionStrategy(),
        )
        super().__init__(*args, **kwargs)


__all__ = ["SingleWikiArticleSectionByIdBase"]
