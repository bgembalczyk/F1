"""General class contracts for refactored base classes."""

import pytest

from complete_extractor.circuits_complete_scraper import F1CompleteCircuitDataExtractor
from complete_extractor.complete_scraper_drivers import CompleteDriverDataExtractor
from complete_extractor.complete_scraper_engines import F1CompleteEngineManufacturerDataExtractor
from complete_extractor.complete_scraper_grands_prix import F1CompleteGrandPrixDataExtractor
from complete_extractor.composite_scraper import CompositeDataExtractor
from complete_extractor.data_extractor import BaseDataExtractor
from scrapers.abc import ABCScraper
from scrapers.single_scraper_engines import SingleEngineManufacturerScraper
from tests.support.refactored_base_classes_utils import assert_issubclass_cases


@pytest.mark.parametrize(
    ("child", "parent"),
    [
        (F1CompleteCircuitDataExtractor, CompositeDataExtractor),
        (F1CompleteGrandPrixDataExtractor, CompositeDataExtractor),
        (CompleteDriverDataExtractor, CompositeDataExtractor),
        (F1CompleteEngineManufacturerDataExtractor, CompositeDataExtractor),
        (CompositeDataExtractor, BaseDataExtractor),
        (SingleEngineManufacturerScraper, ABCScraper),
    ],
)
def test_contract_inheritance(child: type, parent: type) -> None:
    """Core base class inheritance remains intact after refactor."""
    assert_issubclass_cases([(child, parent)])


def test_engine_manufacturer_complete_url() -> None:
    """Engine complete extractor uses list scraper URL config."""
    assert (
        F1CompleteEngineManufacturerDataExtractor.url
        == EngineManufacturersListScraper.CONFIG.url
    )


def test_composite_data_extractor_does_not_inherit_abc_scraper() -> None:
    """Composite extractor is not a web scraper."""
    assert not issubclass(CompositeDataExtractor, ABCScraper)


def test_single_engine_manufacturer_has_extract_by_url_method() -> None:
    """SingleEngineManufacturerScraper keeps extract_by_url contract."""
    assert hasattr(SingleEngineManufacturerScraper, "extract_by_url")
    assert callable(SingleEngineManufacturerScraper.extract_by_url)
