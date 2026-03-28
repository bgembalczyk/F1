from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.circuits.models.services.circuit_service import CircuitService
from scrapers.circuits.single_scraper import F1SingleCircuitScraper
from scrapers.wiki.component_metadata import COMPLETE_SCRAPER_KIND
from scrapers.wiki.component_metadata import build_component_metadata


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
        list_scraper_cls=CircuitsListScraper,
        single_scraper_cls=F1SingleCircuitScraper,
        detail_url_field_path="circuit.url",
        record_postprocessor=CircuitService.normalize_record,
    )


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
