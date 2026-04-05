"""General class contracts for refactored base classes."""

import pytest

from scrapers.base.abc import ABCScraper
from scrapers.base.composite_scraper import CompositeDataExtractor
from scrapers.base.data_extractor import BaseDataExtractor
from scrapers.circuits.complete_scraper import F1CompleteCircuitDataExtractor
from scrapers.drivers.complete_scraper import CompleteDriverDataExtractor
from scrapers.engines.complete_scraper import F1CompleteEngineManufacturerDataExtractor
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper
from scrapers.engines.single_scraper import SingleEngineManufacturerScraper
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixDataExtractor
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
