from abc import ABC

from scrapers.section.selection_strategy.wikipedia_by_id import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.single_wiki_article.single_article_domain_scraper_base import (
    SingleArticleDomainScraperBase,
)


class SingleArticleSectionByIdBase(SingleArticleDomainScraperBase, ABC):
    """Baza używająca strategii sekcji po identyfikatorze."""

    FAMILY_KIND = "single_article"

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault(
            "section_selection_strategy",
            WikipediaSectionByIdSelectionStrategy(),
        )
        super().__init__(*args, **kwargs)


class SingleWikiArticleSectionByIdBase(SingleArticleSectionByIdBase):
    """Backward-compatible alias for legacy naming."""

    FAMILY_KIND = "single_article"


__all__ = [
    "SingleArticleSectionByIdBase",
    "SingleWikiArticleSectionByIdBase",
]
