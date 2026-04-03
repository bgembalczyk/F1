"""Indianapolis-only scraper contract tests."""

import pytest

from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListScraper
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlyConstructorsListScraper,
)
from scrapers.engines.indianapolis_only_engine_manufacturers_list import (
    IndianapolisOnlyEngineManufacturersListScraper,
)
from tests.support.refactored_base_classes_utils import INDIANAPOLIS_CONSTRUCTORS_URL
from tests.support.refactored_base_classes_utils import (
    INDIANAPOLIS_ENGINE_MANUFACTURERS_URL,
)
from tests.support.refactored_base_classes_utils import assert_issubclass_cases


@pytest.mark.parametrize(
    ("child", "parent"),
    [
        (IndianapolisOnlyConstructorsListScraper, IndianapolisOnlyListScraper),
        (
            IndianapolisOnlyEngineManufacturersListScraper,
            IndianapolisOnlyListScraper,
        ),
    ],
)
def test_indianapolis_scrapers_inheritance(child: type, parent: type) -> None:
    """All Indianapolis-only scrapers inherit from the shared base."""
    assert_issubclass_cases([(child, parent)])


def test_indianapolis_section_id_is_set() -> None:
    """Indianapolis base scraper has section id configured."""
    assert IndianapolisOnlyListScraper.section_id == "Indianapolis_500_only"


@pytest.mark.parametrize(
    ("scraper_cls", "expected_url", "record_key", "url_key"),
    [
        (
            IndianapolisOnlyConstructorsListScraper,
            INDIANAPOLIS_CONSTRUCTORS_URL,
            "constructor",
            "constructor_url",
        ),
        (
            IndianapolisOnlyEngineManufacturersListScraper,
            INDIANAPOLIS_ENGINE_MANUFACTURERS_URL,
            "manufacturer",
            "manufacturer_url",
        ),
    ],
)
def test_indianapolis_scraper_config(
    scraper_cls: type,
    expected_url: str,
    record_key: str,
    url_key: str,
) -> None:
    """Each scraper keeps its expected URL and key mapping."""
    scraper = scraper_cls()
    assert scraper.url == expected_url
    assert scraper.record_key == record_key
    assert scraper.url_key == url_key
