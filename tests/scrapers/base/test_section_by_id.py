# ruff: noqa: E501, PLR2004
from unittest.mock import patch

from scrapers.base.single_wiki_article.section_by_id import (
    SingleWikiArticleSectionByIdBase,
)
from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)


class _ConcreteSectionByIdScraper(SingleWikiArticleSectionByIdBase):
    """Minimal concrete subclass for testing."""

    def _assemble_record(self, *args, **kwargs):
        return {}


def _patched_init(self, *args, **kwargs):
    """Replace super().__init__ to avoid HTTP setup."""
    self._kwargs_received = kwargs


def test_section_by_id_sets_default_strategy_when_not_provided() -> None:
    # Lines 13-17: __init__ sets section_selection_strategy via setdefault
    with patch(
        "scrapers.base.single_wiki_article.base.SingleWikiArticleScraperBase.__init__",
        _patched_init,
    ):
        scraper = _ConcreteSectionByIdScraper.__new__(_ConcreteSectionByIdScraper)
        _ConcreteSectionByIdScraper.__init__(scraper)
        assert isinstance(
            scraper._kwargs_received.get("section_selection_strategy"),
            WikipediaSectionByIdSelectionStrategy,
        )


def test_section_by_id_does_not_override_provided_strategy() -> None:
    custom_strategy = WikipediaSectionByIdSelectionStrategy(domain="engines")
    with patch(
        "scrapers.base.single_wiki_article.base.SingleWikiArticleScraperBase.__init__",
        _patched_init,
    ):
        scraper = _ConcreteSectionByIdScraper.__new__(_ConcreteSectionByIdScraper)
        _ConcreteSectionByIdScraper.__init__(
            scraper,
            section_selection_strategy=custom_strategy,
        )
        assert scraper._kwargs_received["section_selection_strategy"] is custom_strategy
