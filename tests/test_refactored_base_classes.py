"""Test refactored base classes to ensure they maintain functionality."""

from scrapers.base.abc import F1Scraper
from scrapers.base.composite_scraper import CompositeScraper
from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListScraper
from scrapers.circuits.complete_scraper import F1CompleteCircuitScraper
from scrapers.constructors.base_constructor_list_scraper import (
    BaseConstructorListScraper,
)
from scrapers.constructors.current_constructors_list import (
    CurrentConstructorsListScraper,
)
from scrapers.constructors.former_constructors_list import FormerConstructorsListScraper
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlyConstructorsListScraper,
)
from scrapers.drivers.complete_scraper import CompleteDriverScraper
from scrapers.engines.complete_scraper import F1CompleteEngineManufacturerScraper
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper
from scrapers.engines.indianapolis_only_engine_manufacturers_list import (
    IndianapolisOnlyEngineManufacturersListScraper,
)
from scrapers.engines.single_scraper import SingleEngineManufacturerScraper
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixScraper
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.points_scoring_systems_history import (
    PointsScoringSystemsHistoryScraper,
)
from scrapers.points.shortened_race_points import ShortenedRacePointsScraper
from scrapers.points.sprint_qualifying_points import SprintQualifyingPointsScraper


class TestIndianapolisOnlyScrapers:
    """Test Indianapolis-only scrapers use the base class correctly."""

    def test_constructors_inherits_from_base(self):
        """Verify IndianapolisOnlyConstructorsListScraper inherits from base."""
        assert issubclass(
            IndianapolisOnlyConstructorsListScraper,
            IndianapolisOnlyListScraper,
        )

    def test_engine_manufacturers_inherits_from_base(self):
        """Verify IndianapolisOnlyEngineManufacturersListScraper inherits from base."""
        assert issubclass(
            IndianapolisOnlyEngineManufacturersListScraper,
            IndianapolisOnlyListScraper,
        )

    def test_section_id_is_set(self):
        """Verify section_id is properly set in base class."""
        assert IndianapolisOnlyListScraper.section_id == "Indianapolis_500_only"

    def test_constructors_has_correct_config(self):
        """Verify constructors scraper has correct configuration."""
        scraper = IndianapolisOnlyConstructorsListScraper()
        assert (
            scraper.url
            == "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"
        )
        assert scraper.record_key == "constructor"
        assert scraper.url_key == "constructor_url"

    def test_engine_manufacturers_has_correct_config(self):
        """Verify engine manufacturers scraper has correct configuration."""
        scraper = IndianapolisOnlyEngineManufacturersListScraper()
        assert (
            scraper.url
            == "https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers"
        )
        assert scraper.record_key == "manufacturer"
        assert scraper.url_key == "manufacturer_url"


class TestCompleteScrapers:
    """Test complete scrapers use CompositeScraper base class correctly."""

    def test_circuit_complete_inherits_from_composite(self):
        """Verify F1CompleteCircuitScraper inherits from CompositeScraper."""
        assert issubclass(F1CompleteCircuitScraper, CompositeScraper)

    def test_grand_prix_complete_inherits_from_composite(self):
        """Verify F1CompleteGrandPrixScraper inherits from CompositeScraper."""
        assert issubclass(F1CompleteGrandPrixScraper, CompositeScraper)

    def test_driver_complete_inherits_from_composite(self):
        """Verify CompleteDriverScraper inherits from CompositeScraper."""
        assert issubclass(CompleteDriverScraper, CompositeScraper)

    def test_engine_manufacturer_complete_inherits_from_composite(self):
        """Verify F1CompleteEngineManufacturerScraper inherits from CompositeScraper."""
        assert issubclass(F1CompleteEngineManufacturerScraper, CompositeScraper)

    def test_engine_manufacturer_complete_url(self):
        """Verify F1CompleteEngineManufacturerScraper uses correct URL."""
        assert (
            F1CompleteEngineManufacturerScraper.url
            == EngineManufacturersListScraper.CONFIG.url
        )


class TestSingleEngineManufacturerScraper:
    """Test SingleEngineManufacturerScraper structure."""

    def test_inherits_from_f1_scraper(self):
        """Verify SingleEngineManufacturerScraper inherits from F1Scraper."""
        assert issubclass(SingleEngineManufacturerScraper, F1Scraper)

    def test_has_fetch_by_url_method(self):
        """Verify SingleEngineManufacturerScraper has fetch_by_url method."""
        assert hasattr(SingleEngineManufacturerScraper, "fetch_by_url")
        assert callable(SingleEngineManufacturerScraper.fetch_by_url)


class TestConstructorListScrapers:
    """Test constructor list scrapers use the base class correctly."""

    def test_current_constructors_inherits_from_base(self):
        """Verify CurrentConstructorsListScraper inherits from base."""
        assert issubclass(CurrentConstructorsListScraper, BaseConstructorListScraper)

    def test_former_constructors_inherits_from_base(self):
        """Verify FormerConstructorsListScraper inherits from base."""
        assert issubclass(FormerConstructorsListScraper, BaseConstructorListScraper)

    def test_base_has_helper_methods(self):
        """Verify base class has expected helper methods."""
        assert hasattr(BaseConstructorListScraper, "build_common_stats_columns")
        assert hasattr(BaseConstructorListScraper, "build_common_metadata_columns")
        assert hasattr(BaseConstructorListScraper, "build_licensed_in_column")
        assert callable(BaseConstructorListScraper.build_common_stats_columns)
        assert callable(BaseConstructorListScraper.build_common_metadata_columns)
        assert callable(BaseConstructorListScraper.build_licensed_in_column)

    def test_common_stats_columns_returns_list(self):
        """Verify build_common_stats_columns returns a list."""
        columns = BaseConstructorListScraper.build_common_stats_columns()
        assert isinstance(columns, list)
        assert len(columns) > 0

    def test_common_metadata_columns_returns_list(self):
        """Verify build_common_metadata_columns returns a list."""
        columns = BaseConstructorListScraper.build_common_metadata_columns()
        assert isinstance(columns, list)
        assert len(columns) > 0


class TestPointsScrapers:
    """Test points scoring scrapers use the base class correctly."""

    def test_sprint_qualifying_inherits_from_base(self):
        """Verify SprintQualifyingPointsScraper inherits from base."""
        assert issubclass(SprintQualifyingPointsScraper, BasePointsScraper)

    def test_shortened_race_inherits_from_base(self):
        """Verify ShortenedRacePointsScraper inherits from base."""
        assert issubclass(ShortenedRacePointsScraper, BasePointsScraper)

    def test_history_inherits_from_base(self):
        """Verify PointsScoringSystemsHistoryScraper inherits from base."""
        assert issubclass(PointsScoringSystemsHistoryScraper, BasePointsScraper)

    def test_base_url_is_set(self):
        """Verify BASE_URL is properly set in base class."""
        expected_url = "https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems"
        assert expected_url == BasePointsScraper.BASE_URL

    def test_scrapers_use_base_url(self):
        """Verify all points scrapers use the BASE_URL."""
        for scraper_class in [
            SprintQualifyingPointsScraper,
            ShortenedRacePointsScraper,
            PointsScoringSystemsHistoryScraper,
        ]:
            assert scraper_class.CONFIG.url == BasePointsScraper.BASE_URL
