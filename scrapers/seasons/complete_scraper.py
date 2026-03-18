from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import BundleRecordWithDetailsStrategy
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from scrapers.seasons.list_scraper import SeasonsListScraper
from scrapers.seasons.single_scraper import SingleSeasonScraper


class CompleteSeasonDataExtractor(CompleteExtractorBase):
    url = SeasonsListScraper.CONFIG.url
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_cls=SeasonsListScraper,
        single_scraper_cls=SingleSeasonScraper,
        detail_url_field_path="season.url",
        record_assembly_strategy=BundleRecordWithDetailsStrategy(
            record_field="season",
            details_key="tables",
        ),
    )


if __name__ == "__main__":
    from scrapers.cli import run_legacy_wrapper

    run_legacy_wrapper("scrapers.seasons.complete_scraper")
