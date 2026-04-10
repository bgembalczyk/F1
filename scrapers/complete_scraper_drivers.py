from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from scrapers.drivers_list_scraper import DriversListScraper
from scrapers.drivers_detail_scraper import DriversDetailScraper
from scrapers.wiki.component_metadata_wiki import COMPLETE_SCRAPER_KIND
from scrapers.wiki.component_metadata_wiki import build_component_metadata


class CompleteDriverDataExtractor(CompleteExtractorBase):
    COMPONENT_METADATA = build_component_metadata(
        domain="drivers",
        kind=COMPLETE_SCRAPER_KIND,
    )
    url = DriversListScraper.CONFIG.url
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(DriversListScraper,),
        single_scraper_cls=DriversDetailScraper,
        detail_url_field_paths=("driver.url",),
    )
