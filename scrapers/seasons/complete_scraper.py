from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import BundleRecordWithDetailsStrategy
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from scrapers.seasons.list_scraper import SeasonsListScraper
from scrapers.seasons.single_scraper import SingleSeasonScraper
from scrapers.wiki.component_metadata import COMPLETE_SCRAPER_KIND
from scrapers.wiki.component_metadata import build_component_metadata


class CompleteSeasonDataExtractor(CompleteExtractorBase):
    COMPONENT_METADATA = build_component_metadata(
        domain="seasons",
        kind=COMPLETE_SCRAPER_KIND,
    )
    url = SeasonsListScraper.CONFIG.url
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(SeasonsListScraper,),
        single_scraper_cls=SingleSeasonScraper,
        detail_url_field_paths=("season.url",),
        record_assembly_strategy=BundleRecordWithDetailsStrategy(
            record_field="season",
            details_key="tables",
        ),
    )


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
