"""Wiki scraper hierarchy tests."""

import pytest

from scrapers.abc import ABCScraper
from scrapers.base.table.scraper import F1TableScraper
from scrapers.circuits.circuits_single_scraper import F1SingleCircuitScraper
from scrapers.constructors_single_scraper import SingleConstructorScraper
from scrapers.drivers.single_scraper_drivers import SingleDriverScraper
from scrapers.engines.single_scraper_engines import SingleEngineManufacturerScraper
from scrapers.list.base import F1ListScraper
from scrapers.parsers.infobox.circuit import F1CircuitInfoboxParser
from scrapers.parsers.wiki.infobox import WikiInfoboxParser
from scrapers.parsers.wiki.table import WikiTableParser
from scrapers.scraper_sponsorship_liveries import F1SponsorshipLiveriesScraper
from scrapers.scraper_wiki import WikiScraper
from scrapers.single_scraper_grands_prix import F1SingleGrandPrixScraper
from scrapers.single_scraper_seasons import SingleSeasonScraper
from scrapers.standings_scraper_seasons import F1StandingsScraper
from scrapers.standings_scraper_seasons import F1StandingsTableParser
from tests.support.refactored_base_classes_utils import assert_issubclass_cases
from tests.support.refactored_base_classes_utils import assert_not_issubclass_cases


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
        (F1StandingsTableParser, WikiTableParser),
        (F1StandingsScraper, F1TableScraper),
    ],
)
def test_wiki_hierarchy_issubclass_cases(child: type, parent: type) -> None:
    """Wiki hierarchy and transitive inheritance checks."""
    assert_issubclass_cases([(child, parent)])


@pytest.mark.parametrize(
    ("child", "parent"),
    [
        (F1CircuitInfoboxParser, WikiScraper),
        (F1StandingsTableParser, WikiScraper),
        (F1StandingsTableParser, F1TableScraper),
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


def test_wiki_element_parser_mixin_is_part_of_wiki_scraper_api() -> None:
    """WikiScraper keeps WikiElementParserMixin in its public MRO."""
    assert WikiElementParserMixin in WikiScraper.__mro__


def test_wiki_scraper_has_scrape_method() -> None:
    """WikiScraper still offers scrape(url)."""
    assert hasattr(WikiScraper, "scrape")
    assert callable(WikiScraper.scrape)


def test_standings_scraper_has_fetch_parse_pipeline() -> None:
    """Każdy Scraper implementuje pipeline fetch/parse."""
    assert hasattr(F1StandingsScraper, "fetch")
    assert callable(F1StandingsScraper.fetch)
    assert hasattr(F1StandingsScraper, "parse")
    assert callable(F1StandingsScraper.parse)
