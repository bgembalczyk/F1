# ruff: noqa: E501, PLR2004
from unittest.mock import patch

from scrapers.single_wiki_article import WikipediaSectionByIdSelectionStrategy
from tests.scrapers.base.dummy_classes import ConcreteSectionByIdScraper
from tests.scrapers.base.test_helpers import patched_article_init


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
