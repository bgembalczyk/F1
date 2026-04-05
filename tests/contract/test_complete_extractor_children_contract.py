import pytest

from scrapers.circuits.complete_scraper import F1CompleteCircuitDataExtractor
from scrapers.constructors.complete_scraper import CompleteConstructorsDataExtractor
from scrapers.drivers.complete_scraper import CompleteDriverDataExtractor
from scrapers.engines.complete_scraper import F1CompleteEngineManufacturerDataExtractor
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixDataExtractor
from scrapers.seasons.complete_scraper import CompleteSeasonDataExtractor


@pytest.mark.parametrize(
    "extractor_cls",
    [
        F1CompleteCircuitDataExtractor,
        CompleteConstructorsDataExtractor,
        CompleteDriverDataExtractor,
        F1CompleteEngineManufacturerDataExtractor,
        F1CompleteGrandPrixDataExtractor,
        CompleteSeasonDataExtractor,
    ],
)
def test_complete_extractor_children_implement_base_protocols(extractor_cls) -> None:
    list_scraper_classes = extractor_cls.DOMAIN_CONFIG.list_scraper_classes
    single_scraper_cls = extractor_cls.DOMAIN_CONFIG.single_scraper_cls

    assert list_scraper_classes
    assert all(
        callable(getattr(scraper_cls, "fetch", None))
        for scraper_cls in list_scraper_classes
    )
    assert single_scraper_cls is not None
    assert callable(getattr(single_scraper_cls, "extract_by_url", None))
