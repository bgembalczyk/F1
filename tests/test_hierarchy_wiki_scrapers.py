"""Wiki scraper hierarchy tests."""

import pytest

from scrapers.base.abc import ABCScraper
from scrapers.base.list.scraper import F1ListScraper
from scrapers.base.table.scraper import F1TableScraper
from scrapers.circuits.infobox.scraper import F1CircuitInfoboxParser
from scrapers.circuits.single_scraper import F1SingleCircuitScraper
from scrapers.constructors.single_scraper import SingleConstructorScraper
from scrapers.drivers.single_scraper import SingleDriverScraper
from scrapers.engines.single_scraper import SingleEngineManufacturerScraper
from scrapers.grands_prix.single_scraper import F1SingleGrandPrixScraper
from scrapers.seasons.single_scraper import SingleSeasonScraper
from scrapers.seasons.standings_scraper import F1StandingsScraper
from scrapers.sponsorship_liveries.scraper import F1SponsorshipLiveriesScraper
from scrapers.wiki.parsers.elements.infobox import InfoboxParser as WikiInfoboxParser
from scrapers.wiki.parsers.elements.table import TableParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import WikiElementParserMixin
from scrapers.wiki.scraper import WikiScraper
from tests.support.refactored_base_classes_utils import (
    assert_issubclass_cases,
    assert_not_issubclass_cases,
)


@pytest.mark.parametrize(
    ("child", "parent"),
    [
        (WikiScraper, ABCScraper),
        (F1ListScraper, WikiScraper),
        (F1TableScraper, WikiScraper),
        (F1SingleCircuitScraper, WikiScraper),
        (SingleConstructorScraper, WikiScraper),
        (SingleDriverScraper, WikiScraper),
        (SingleSeasonScraper, WikiScraper),
        (SingleEngineManufacturerScraper, WikiScraper),
        (F1SingleGrandPrixScraper, WikiScraper),
        (F1SponsorshipLiveriesScraper, WikiScraper),
        (F1ListScraper, ABCScraper),
        (F1TableScraper, ABCScraper),
        (F1SingleCircuitScraper, ABCScraper),
        (SingleConstructorScraper, ABCScraper),
        (SingleDriverScraper, ABCScraper),
        (SingleSeasonScraper, ABCScraper),
        (SingleEngineManufacturerScraper, ABCScraper),
        (F1SingleGrandPrixScraper, ABCScraper),
        (F1CircuitInfoboxParser, WikiInfoboxParser),
        (WikiScraper, WikiElementParserMixin),
        (F1StandingsScraper, TableParser),
    ],
)
def test_wiki_hierarchy_issubclass_cases(child: type, parent: type) -> None:
    """Wiki hierarchy and transitive inheritance checks."""
    assert_issubclass_cases([(child, parent)])


@pytest.mark.parametrize(
    ("child", "parent"),
    [
        (F1CircuitInfoboxParser, WikiScraper),
        (F1StandingsScraper, WikiScraper),
        (F1StandingsScraper, F1TableScraper),
    ],
)
def test_wiki_hierarchy_not_issubclass_cases(child: type, parent: type) -> None:
    """Explicit non-inheritance checks for parser-only classes."""
    assert_not_issubclass_cases([(child, parent)])


def test_wiki_scraper_has_wiki_parsers() -> None:
    """WikiScraper exposes high-level parser components."""
    scraper = WikiScraper()
    assert hasattr(scraper, "header_parser")
    assert hasattr(scraper, "body_content_parser")
    assert hasattr(scraper, "section_parser")


def test_wiki_scraper_has_element_parsers_from_mixin() -> None:
    """WikiScraper exposes parser attributes from WikiElementParserMixin."""
    scraper = WikiScraper()
    assert hasattr(scraper, "table_parser")
    assert hasattr(scraper, "infobox_parser")
    assert hasattr(scraper, "list_parser")
    assert hasattr(scraper, "paragraph_parser")


def test_wiki_element_parser_mixin_has_find_infobox_helpers() -> None:
    """WikiElementParserMixin keeps helper methods available."""
    assert hasattr(WikiElementParserMixin, "find_infobox")
    assert hasattr(WikiElementParserMixin, "find_infoboxes")
    assert callable(WikiElementParserMixin.find_infobox)
    assert callable(WikiElementParserMixin.find_infoboxes)


def test_wiki_scraper_has_scrape_method() -> None:
    """WikiScraper still offers scrape(url)."""
    assert hasattr(WikiScraper, "scrape")
    assert callable(WikiScraper.scrape)


def test_standings_scraper_has_parse_method() -> None:
    """F1StandingsScraper still exposes parse(element)."""
    assert hasattr(F1StandingsScraper, "parse")
    assert callable(F1StandingsScraper.parse)
