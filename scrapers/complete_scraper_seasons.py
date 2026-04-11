from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from record_assembly_strategy.bundle_record_with_details import (
    BundleRecordWithDetailsStrategy,
)
from scrapers.component_metadata_wiki import COMPLETE_SCRAPER_KIND
from scrapers.component_metadata_wiki import build_component_metadata
from scrapers.seasons.list_scraper import SeasonsListScraper
from scrapers.seasons.single_scraper import SeasonsDetailScraper


class CompleteSeasonDataExtractor(CompleteExtractorBase):
    COMPONENT_METADATA = build_component_metadata(
        domain="seasons",
        kind=COMPLETE_SCRAPER_KIND,
    )
    url = SeasonsListScraper.CONFIG.url
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(SeasonsListScraper,),
        single_scraper_cls=SeasonsDetailScraper,
        detail_url_field_paths=("season.url",),
        record_assembly_strategy=BundleRecordWithDetailsStrategy(
            record_field="season",
            details_key="tables",
        ),
    )
