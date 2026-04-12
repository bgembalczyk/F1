from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from scrapers.component_metadata_wiki import COMPLETE_SCRAPER_KIND
from scrapers.component_metadata_wiki import build_component_metadata
from scrapers.single_scraper_drivers import SingleDriverScraper
from scrapers.list_scraper_drivers import F1DriversListScraper


class CompleteDriverDataExtractor(CompleteExtractorBase):
    COMPONENT_METADATA = build_component_metadata(
        domain="drivers",
        kind=COMPLETE_SCRAPER_KIND,
    )
    url = F1DriversListScraper.CONFIG.url
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(F1DriversListScraper,),
        single_scraper_cls=SingleDriverScraper,
        detail_url_field_paths=("driver.url",),
    )
