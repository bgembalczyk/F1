from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from scrapers.circuits.list_scraper_circuits import CircuitsListScraper
from scrapers.circuits.single_scraper_circuits import CircuitsDetailScraper
from scrapers.component_metadata_wiki import COMPLETE_SCRAPER_KIND
from scrapers.component_metadata_wiki import build_component_metadata
from scrapers.services.circuit import CircuitService


class F1CompleteCircuitDataExtractor(CompleteExtractorBase):
    """
    Pobiera listę torów, a następnie zaciąga szczegóły każdego toru (infobox + tabele),
    po czym normalizuje rekord do docelowej struktury.

    Dla torów, których artykuł nie ma "circuit/racetrack"-podobnych kategorii,
    pole `details` będzie miało wartość None, a `layouts` / `history` / `location`
    mogą być puste.
    """

    COMPONENT_METADATA = build_component_metadata(
        domain="circuits",
        kind=COMPLETE_SCRAPER_KIND,
    )
    url = CircuitsListScraper.CONFIG.url
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(CircuitsListScraper,),
        single_scraper_cls=CircuitsDetailScraper,
        detail_url_field_paths=("circuit.url",),
        record_postprocessor=CircuitService.normalize_record,
    )
