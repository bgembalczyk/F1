from abc import ABC

from scrapers.section.selection_strategy.wikipedia_by_id import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.single_wiki_article.single_article_scraper_base import ArticleScraperBase


class SectionByIdScraperBase(ArticleScraperBase, ABC):
    """Base for article scrapers using section-id selection strategy."""

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault(
            "section_selection_strategy",
            WikipediaSectionByIdSelectionStrategy(),
        )
        super().__init__(*args, **kwargs)


__all__ = [
    "SectionByIdScraperBase",
]
