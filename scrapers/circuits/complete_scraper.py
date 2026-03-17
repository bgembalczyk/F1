from scrapers.base.complete_extractor_base import CompleteExtractorBase
from scrapers.base.complete_extractor_base import CompleteExtractorDomainConfig
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.circuits.models.services.circuit_service import CircuitService
from scrapers.circuits.single_scraper import F1SingleCircuitScraper


class F1CompleteCircuitDataExtractor(CompleteExtractorBase):
    """
    Pobiera listę torów, a następnie zaciąga szczegóły każdego toru (infobox + tabele),
    po czym normalizuje rekord do docelowej struktury.

    Dla torów, których artykuł nie ma "circuit/racetrack"-podobnych kategorii,
    pole `details` będzie miało wartość None, a `layouts` / `history` / `location`
    mogą być puste.
    """

    url = CircuitsListScraper.CONFIG.url
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_cls=CircuitsListScraper,
        single_scraper_cls=F1SingleCircuitScraper,
        detail_url_field_path="circuit.url",
        record_postprocessor=CircuitService.normalize_record,
    )


if __name__ == "__main__":
    from scrapers.cli import run_legacy_wrapper

    run_legacy_wrapper("scrapers.circuits.complete_scraper")
