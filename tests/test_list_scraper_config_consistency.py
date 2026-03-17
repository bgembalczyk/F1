from __future__ import annotations

from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.constructors.current_constructors_list import CurrentConstructorsListScraper
from scrapers.drivers.list_scraper import F1DriversListScraper
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper
from scrapers.points.points_scoring_systems_history import PointsScoringSystemsHistoryScraper

LIST_SCRAPERS = (
    CircuitsListScraper,
    GrandsPrixListScraper,
    CurrentConstructorsListScraper,
    F1DriversListScraper,
    PointsScoringSystemsHistoryScraper,
    EngineManufacturersListScraper,
)


def test_list_scrapers_have_minimal_config_contract() -> None:
    for scraper_cls in LIST_SCRAPERS:
        config = scraper_cls.CONFIG
        assert config is not None, f"Missing CONFIG in {scraper_cls.__name__}"
        assert isinstance(config.url, str) and config.url.startswith("https://")
        assert config.section_id, f"Missing section_id in {scraper_cls.__name__}"
        assert config.expected_headers, f"Missing expected_headers in {scraper_cls.__name__}"
        assert config.columns, f"Missing columns mapping in {scraper_cls.__name__}"
        assert config.record_factory is not None, f"Missing record_factory in {scraper_cls.__name__}"


def test_list_scrapers_have_domain_profile_contract() -> None:
    for scraper_cls in LIST_SCRAPERS:
        assert getattr(scraper_cls, "options_domain", None)
        assert getattr(scraper_cls, "options_profile", None)
