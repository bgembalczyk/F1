# ruff: noqa: E501, PLR2004
from unittest.mock import patch

from scrapers.single_wiki_article import SectionByIdScraperBase
from scrapers.single_wiki_article import WikipediaSectionByIdSelectionStrategy
from scrapers.single_wiki_article.single_article_section_aware_mixin import (
    SectionAwareMixin,
)


class ConcreteSectionByIdScraper(SectionByIdScraperBase):
    """Minimal concrete subclass for testing."""

    def _assemble_record(self, *_args, **_kwargs):
        return {}


def patched_article_init(self, *_args, **kwargs):
    """Replace ArticleScraperBase.__init__ to avoid HTTP setup."""
    pass


def test_section_by_id_sets_default_strategy_when_not_provided() -> None:
    with patch(
        "scrapers.single_wiki_article.single_article_scraper_base.ArticleScraperBase.__init__",
        patched_article_init,
    ):
        scraper = ConcreteSectionByIdScraper.__new__(ConcreteSectionByIdScraper)
        ConcreteSectionByIdScraper.__init__(scraper)
        assert isinstance(
            scraper.section_selection_strategy,
            WikipediaSectionByIdSelectionStrategy,
        )


def test_section_by_id_does_not_override_provided_strategy() -> None:
    custom_strategy = WikipediaSectionByIdSelectionStrategy(domain="engines")
    with patch(
        "scrapers.single_wiki_article.single_article_scraper_base.ArticleScraperBase.__init__",
        patched_article_init,
    ):
        scraper = ConcreteSectionByIdScraper.__new__(ConcreteSectionByIdScraper)
        ConcreteSectionByIdScraper.__init__(
            scraper,
            section_selection_strategy=custom_strategy,
        )
        assert scraper.section_selection_strategy is custom_strategy
