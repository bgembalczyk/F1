"""Test refactored base classes to ensure they maintain functionality."""

from scrapers.base.abc import ABCScraper
from scrapers.base.composite_scraper import CompositeDataExtractor
from scrapers.base.data_extractor import BaseDataExtractor
from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListScraper
from scrapers.base.list.scraper import F1ListScraper
from scrapers.base.table.scraper import F1TableScraper
from scrapers.circuits.complete_scraper import F1CompleteCircuitDataExtractor
from scrapers.circuits.infobox.scraper import F1CircuitInfoboxParser
from scrapers.circuits.single_scraper import F1SingleCircuitScraper
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
from scrapers.constructors.single_scraper import SingleConstructorScraper
from scrapers.drivers.complete_scraper import CompleteDriverDataExtractor
from scrapers.drivers.single_scraper import SingleDriverScraper
from scrapers.engines.complete_scraper import F1CompleteEngineManufacturerDataExtractor
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper
from scrapers.engines.indianapolis_only_engine_manufacturers_list import (
    IndianapolisOnlyEngineManufacturersListScraper,
)
from scrapers.engines.single_scraper import SingleEngineManufacturerScraper
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixDataExtractor
from scrapers.grands_prix.single_scraper import F1SingleGrandPrixScraper
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.points_scoring_systems_history import (
    PointsScoringSystemsHistoryScraper,
)
from scrapers.points.shortened_race_points import ShortenedRacePointsScraper
from scrapers.points.sprint_qualifying_points import SprintQualifyingPointsScraper
from scrapers.seasons.single_scraper import SingleSeasonScraper
from scrapers.seasons.standings_scraper import F1StandingsScraper
from scrapers.sponsorship_liveries.scraper import F1SponsorshipLiveriesScraper
from scrapers.wiki.scraper import WikiScraper
from scrapers.wiki.parsers.elements.infobox import InfoboxParser as WikiInfoboxParser


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
    """Test complete data extractors use CompositeDataExtractor / BaseDataExtractor correctly."""

    def test_circuit_complete_inherits_from_composite(self):
        """Verify F1CompleteCircuitDataExtractor inherits from CompositeDataExtractor."""
        assert issubclass(F1CompleteCircuitDataExtractor, CompositeDataExtractor)

    def test_grand_prix_complete_inherits_from_composite(self):
        """Verify F1CompleteGrandPrixDataExtractor inherits from CompositeDataExtractor."""
        assert issubclass(F1CompleteGrandPrixDataExtractor, CompositeDataExtractor)

    def test_driver_complete_inherits_from_composite(self):
        """Verify CompleteDriverDataExtractor inherits from CompositeDataExtractor."""
        assert issubclass(CompleteDriverDataExtractor, CompositeDataExtractor)

    def test_engine_manufacturer_complete_inherits_from_composite(self):
        """Verify F1CompleteEngineManufacturerDataExtractor inherits from CompositeDataExtractor."""
        assert issubclass(
            F1CompleteEngineManufacturerDataExtractor, CompositeDataExtractor
        )

    def test_engine_manufacturer_complete_url(self):
        """Verify F1CompleteEngineManufacturerDataExtractor uses correct URL."""
        assert (
            F1CompleteEngineManufacturerDataExtractor.url
            == EngineManufacturersListScraper.CONFIG.url
        )

    def test_composite_data_extractor_inherits_base_data_extractor(self):
        """Verify CompositeDataExtractor inherits from BaseDataExtractor."""
        assert issubclass(CompositeDataExtractor, BaseDataExtractor)

    def test_composite_data_extractor_does_not_inherit_abc_scraper(self):
        """Verify CompositeDataExtractor does NOT inherit from ABCScraper."""
        assert not issubclass(CompositeDataExtractor, ABCScraper)


class TestSingleEngineManufacturerScraper:
    """Test SingleEngineManufacturerScraper structure."""

    def test_inherits_from_f1_scraper(self):
        """Verify SingleEngineManufacturerScraper inherits from ABCScraper."""
        assert issubclass(SingleEngineManufacturerScraper, ABCScraper)

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


class TestWikiScraperHierarchy:
    """Test WikiScraper hierarchy – WikiScraper inherits ABCScraper,
    ListScrapers and SingleScrapers inherit WikiScraper."""

    def test_wiki_scraper_inherits_from_f1_scraper(self):
        """Verify WikiScraper inherits from ABCScraper."""
        assert issubclass(WikiScraper, ABCScraper)

    # ---------- F1ListScraper ----------

    def test_f1_list_scraper_inherits_from_wiki_scraper(self):
        """Verify F1ListScraper inherits from WikiScraper."""
        assert issubclass(F1ListScraper, WikiScraper)

    # ---------- F1TableScraper ----------

    def test_f1_table_scraper_inherits_from_wiki_scraper(self):
        """Verify F1TableScraper inherits from WikiScraper."""
        assert issubclass(F1TableScraper, WikiScraper)

    # ---------- Single scrapers ----------

    def test_single_circuit_scraper_inherits_from_wiki_scraper(self):
        """Verify F1SingleCircuitScraper inherits from WikiScraper."""
        assert issubclass(F1SingleCircuitScraper, WikiScraper)

    def test_single_constructor_scraper_inherits_from_wiki_scraper(self):
        """Verify SingleConstructorScraper inherits from WikiScraper."""
        assert issubclass(SingleConstructorScraper, WikiScraper)

    def test_single_driver_scraper_inherits_from_wiki_scraper(self):
        """Verify SingleDriverScraper inherits from WikiScraper."""
        assert issubclass(SingleDriverScraper, WikiScraper)

    def test_single_season_scraper_inherits_from_wiki_scraper(self):
        """Verify SingleSeasonScraper inherits from WikiScraper."""
        assert issubclass(SingleSeasonScraper, WikiScraper)

    def test_single_engine_manufacturer_inherits_from_wiki_scraper(self):
        """Verify SingleEngineManufacturerScraper inherits from WikiScraper."""
        assert issubclass(SingleEngineManufacturerScraper, WikiScraper)

    def test_single_grand_prix_scraper_inherits_from_wiki_scraper(self):
        """Verify F1SingleGrandPrixScraper inherits from WikiScraper."""
        assert issubclass(F1SingleGrandPrixScraper, WikiScraper)

    def test_circuit_infobox_parser_is_not_wiki_scraper(self):
        """Verify F1CircuitInfoboxParser is a pure parser, not a WikiScraper."""
        assert not issubclass(F1CircuitInfoboxParser, WikiScraper)

    def test_circuit_infobox_parser_inherits_from_infobox_parser(self):
        """Verify F1CircuitInfoboxParser inherits from InfoboxParser."""
        assert issubclass(F1CircuitInfoboxParser, WikiInfoboxParser)

    def test_sponsorship_liveries_scraper_inherits_from_wiki_scraper(self):
        """Verify F1SponsorshipLiveriesScraper inherits from WikiScraper."""
        assert issubclass(F1SponsorshipLiveriesScraper, WikiScraper)

    # ---------- Transitivity through WikiScraper ----------

    def test_list_scraper_still_inherits_f1_scraper(self):
        """Verify F1ListScraper (transitively) inherits from ABCScraper."""
        assert issubclass(F1ListScraper, ABCScraper)

    def test_table_scraper_still_inherits_f1_scraper(self):
        """Verify F1TableScraper (transitively) inherits from ABCScraper."""
        assert issubclass(F1TableScraper, ABCScraper)

    def test_single_scrapers_still_inherit_f1_scraper(self):
        """Verify all single scrapers (transitively) inherit from ABCScraper."""
        for cls in [
            F1SingleCircuitScraper,
            SingleConstructorScraper,
            SingleDriverScraper,
            SingleSeasonScraper,
            SingleEngineManufacturerScraper,
            F1SingleGrandPrixScraper,
        ]:
            assert issubclass(cls, ABCScraper), (
                f"{cls.__name__} should (transitively) inherit ABCScraper"
            )

    def test_wiki_scraper_has_wiki_parsers(self):
        """Verify WikiScraper exposes HeaderParser, BodyContentParser and SectionParser as attributes."""
        scraper = WikiScraper()
        assert hasattr(scraper, "header_parser")
        assert hasattr(scraper, "body_content_parser")
        assert hasattr(scraper, "section_parser")

    def test_wiki_scraper_has_scrape_method(self):
        """Verify WikiScraper has a scrape(url) convenience method."""
        assert hasattr(WikiScraper, "scrape")
        assert callable(WikiScraper.scrape)


class TestF1StandingsScraper:
    """Test that F1StandingsScraper is a pure parser, not a WikiScraper."""

    def test_standings_scraper_is_not_wiki_scraper(self):
        """Verify F1StandingsScraper does not inherit from WikiScraper."""
        assert not issubclass(F1StandingsScraper, WikiScraper)

    def test_standings_scraper_is_not_f1_table_scraper(self):
        """Verify F1StandingsScraper does not inherit from F1TableScraper."""
        assert not issubclass(F1StandingsScraper, F1TableScraper)

    def test_standings_scraper_has_parse_method(self):
        """Verify F1StandingsScraper exposes a parse(soup) method."""
        assert hasattr(F1StandingsScraper, "parse")
        assert callable(F1StandingsScraper.parse)
