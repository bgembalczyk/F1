import pytest

from complete_extractor.circuits_complete_scraper import F1CompleteCircuitDataExtractor
from complete_extractor.complete_scraper_drivers import CompleteDriverDataExtractor
from complete_extractor.complete_scraper_engines import F1CompleteEngineManufacturerDataExtractor
from complete_extractor.complete_scraper_grands_prix import F1CompleteGrandPrixDataExtractor
from complete_extractor.complete_scraper_seasons import CompleteSeasonDataExtractor
from complete_extractor.constructors_complete_scraper import CompleteConstructorsDataExtractor


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
